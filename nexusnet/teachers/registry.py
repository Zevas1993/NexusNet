from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from nexus.models import ModelRegistry

from ..schemas import (
    AttachedTeacher,
    IndependenceMetrics,
    ModelAttachRequest,
    TeacherArbitrationRecord,
    TeacherAssignment,
    TeacherProfile,
    TeacherRetirementDecision,
)
from .loader import TeacherCatalogLoader
from .benchmarks import TeacherBenchmarkRegistry
from .cohort_thresholds import TeacherCohortThresholdRegistry
from .fleet_registry import TeacherBenchmarkFleetRegistry
from .fleet_windows import TeacherFleetWindowRegistry
from .schema_versions import TeacherSchemaRegistry
from .provenance import teacher_provenance_payload
from .retirement import TeacherRetirementAdvisor
from .routing import TeacherRoutingContext, TeacherRoutingPolicyEngine

if TYPE_CHECKING:
    from nexusnet.core import NexusBrain


class TeacherRegistry:
    def __init__(self, model_registry: ModelRegistry, config_dir: Path):
        self.model_registry = model_registry
        self.catalog = TeacherCatalogLoader(config_dir).load()
        self.status_label = self.catalog.status_label
        self.schema_version = self.catalog.schema_version
        self.migration_notes = self.catalog.migration_notes
        self.default_registry_layer = self.catalog.default_registry_layer
        self.core_mentor_ensemble = self.catalog.core_mentor_ensemble
        self.expert_roster = self.catalog.expert_roster
        self.regimens = self.catalog.regimens
        self.routing_policy = self.catalog.routing_policy
        self.registry_layers = self.catalog.registry_layers
        self.benchmark_registry = TeacherBenchmarkRegistry(config_dir)
        self.threshold_registry = self.benchmark_registry.thresholds
        self.fleet_registry = TeacherBenchmarkFleetRegistry(config_dir)
        self.fleet_window_registry = TeacherFleetWindowRegistry(config_dir)
        self.cohort_threshold_registry = TeacherCohortThresholdRegistry()
        self.schema_registry = TeacherSchemaRegistry(config_dir)
        self.schema_manifest_path: str | None = None
        self._profiles = {profile.teacher_id: profile for profile in self.catalog.profiles}
        self._assignments = {(assignment.subject, assignment.registry_layer): assignment for assignment in self.catalog.assignments}
        self._attached: dict[str, AttachedTeacher] = {}
        self._active_teacher_id: str | None = None
        self._routing = TeacherRoutingPolicyEngine(self.routing_policy)
        self._retirement_advisor = TeacherRetirementAdvisor()

    def list_profiles(self) -> list[TeacherProfile]:
        return sorted((self._hydrate_profile(profile) for profile in self._profiles.values()), key=lambda profile: profile.teacher_id)

    def list_assignments(self) -> list[TeacherAssignment]:
        return sorted(
            self._assignments.values(),
            key=lambda assignment: (
                assignment.auxiliary,
                assignment.roster_position or 999,
                assignment.subject,
                assignment.registry_layer,
            ),
        )

    def list_attached(self) -> list[AttachedTeacher]:
        return sorted(self._attached.values(), key=lambda attachment: attachment.teacher_id)

    def active_teacher(self) -> AttachedTeacher | None:
        if not self._active_teacher_id:
            return None
        return self._attached.get(self._active_teacher_id)

    def assignment_for(self, subject: str, registry_layer: str | None = None) -> TeacherAssignment | None:
        if registry_layer:
            return self._assignments.get((subject, registry_layer))
        return self._assignments.get((subject, self.default_registry_layer)) or self._assignments.get((subject, "historical"))

    def regimen_for_subject(self, subject: str) -> dict[str, Any] | None:
        for _, payload in self.regimens.get("expert_regimens", {}).items():
            if payload.get("subject") == subject:
                return payload
        return None

    def set_active(self, teacher_id: str) -> AttachedTeacher | None:
        attached = self._attached.get(teacher_id)
        if not attached:
            return None
        for candidate_id, candidate in list(self._attached.items()):
            self._attached[candidate_id] = candidate.model_copy(update={"active": candidate_id == teacher_id})
        self._active_teacher_id = teacher_id
        return self._attached[teacher_id]

    def attach(
        self,
        brain: NexusBrain,
        request: ModelAttachRequest,
        *,
        registry_layer: str | None = None,
        routing_decision: Any | None = None,
        arbitration: TeacherArbitrationRecord | None = None,
        lineage: str = "live-derived",
        benchmark_family: str | None = None,
        native_takeover_candidate_id: str | None = None,
    ) -> AttachedTeacher:
        profile = self._resolve_profile(request.teacher_id, request.model_hint)
        if profile is None:
            registration = self.model_registry.resolve_model(request.model_hint or "mock/default")
            adapter = brain.attach_base_model(registration.model_id, role=request.attach_role)
            attached = AttachedTeacher(
                teacher_id=f"adhoc::{registration.model_id}",
                model_id=registration.model_id,
                attach_role=request.attach_role,
                active=request.set_active,
                status_label="IMPLEMENTATION BRANCH",
                provenance={
                    "teacher_id": f"adhoc::{registration.model_id}",
                    "canonical_name": registration.display_name,
                    "status_label": "IMPLEMENTATION BRANCH",
                    "lineage": "Ad hoc model attachment outside canonical teacher payload.",
                    "role": request.attach_role,
                    "model_hint": request.model_hint,
                    "registry_layer": registry_layer or "adhoc",
                    "selected_teachers": [f"adhoc::{registration.model_id}"],
                    "selected_teacher_roles": {"primary": f"adhoc::{registration.model_id}"},
                    "capability_profile": adapter.capability_profile().model_dump(mode="json"),
                },
            )
            self._attached[attached.teacher_id] = attached
            if request.set_active:
                self.set_active(attached.teacher_id)
            return self._attached[attached.teacher_id]

        resolved_model_hint = request.model_hint or next(iter(profile.model_hints), None) or "mock/default"
        registration = self.model_registry.resolve_model(resolved_model_hint)
        adapter = brain.attach_base_model(registration.model_id, role=request.attach_role)
        selected_layer = registry_layer or self._default_registry_layer_for_profile(profile)
        subject_for_threshold = (
            getattr(routing_decision, "subject", None)
            or (arbitration.expert if arbitration is not None else None)
            or (profile.role_tags[0] if profile.role_tags else None)
        )
        threshold_set_id = None
        if benchmark_family and subject_for_threshold:
            try:
                threshold_set_id = self.threshold_registry.resolve(
                    subject=subject_for_threshold,
                    benchmark_family=benchmark_family,
                ).threshold_set_id
            except Exception:
                threshold_set_id = None
        attached = AttachedTeacher(
            teacher_id=profile.teacher_id,
            model_id=registration.model_id,
            attach_role=request.attach_role,
            active=request.set_active,
            status_label=profile.status_label,
            provenance=teacher_provenance_payload(
                profile=profile,
                model_id=registration.model_id,
                attach_role=request.attach_role,
                capability_profile=adapter.capability_profile().model_dump(mode="json"),
                registry_layer=selected_layer,
                routing_decision=routing_decision,
                arbitration=arbitration,
                lineage=lineage,
                benchmark_family=benchmark_family,
                threshold_set_id=threshold_set_id,
                native_takeover_candidate_id=native_takeover_candidate_id,
            ),
        )
        self._attached[profile.teacher_id] = attached
        if request.set_active:
            self.set_active(profile.teacher_id)
        return self._attached[profile.teacher_id]

    def resolve_for_task(
        self,
        *,
        brain: NexusBrain,
        task_type: str,
        expert: str | None,
        requested_teacher_id: str | None = None,
        model_hint: str | None = None,
        routing_metadata: dict[str, Any] | None = None,
    ) -> tuple[AttachedTeacher, TeacherArbitrationRecord]:
        routing_metadata = routing_metadata or {}
        requested_registry_layer = routing_metadata.get("teacher_registry_layer")
        benchmark_family = routing_metadata.get("benchmark_family")
        lineage = routing_metadata.get("teacher_lineage", "live-derived")
        native_takeover_candidate_id = routing_metadata.get("native_takeover_candidate_id")

        if requested_teacher_id or model_hint:
            explicit_profile = self._resolve_profile(requested_teacher_id, model_hint)
            explicit_layer = requested_registry_layer or (self._default_registry_layer_for_profile(explicit_profile) if explicit_profile else self.default_registry_layer)
            record = TeacherArbitrationRecord(
                task_type=task_type,
                expert=expert,
                registry_layer=explicit_layer,
                candidates=[requested_teacher_id or model_hint or "adhoc"],
                selected_teacher_id=requested_teacher_id or (explicit_profile.teacher_id if explicit_profile else f"adhoc::{model_hint}"),
                selected_teacher_ids=[requested_teacher_id or (explicit_profile.teacher_id if explicit_profile else f"adhoc::{model_hint}")],
                selected_roles={"primary": requested_teacher_id or (explicit_profile.teacher_id if explicit_profile else f"adhoc::{model_hint}")},
                local_vs_remote=self._local_vs_remote(explicit_profile.teacher_id) if explicit_profile else "local",
                arbitration_result="SELECT_BEST",
                benchmark_family=benchmark_family,
                teacher_confidence=0.95,
                dream_lineage=lineage,
                native_takeover_candidate_id=native_takeover_candidate_id,
                rationale="Explicit teacher/model request takes precedence.",
            )
            attached = self.attach(
                brain,
                ModelAttachRequest(
                    teacher_id=requested_teacher_id,
                    model_hint=model_hint,
                    attach_role="teacher",
                    set_active=True,
                ),
                registry_layer=explicit_layer,
                arbitration=record,
                lineage=lineage,
                benchmark_family=benchmark_family,
                native_takeover_candidate_id=native_takeover_candidate_id,
            )
            self._update_attached_provenance(attached.teacher_id, arbitration=record, routing_decision=None)
            return self._attached[attached.teacher_id], record

        subject = expert or "core-brain"
        context = TeacherRoutingContext(
            subject=subject,
            task_type=task_type,
            budget_class=str(routing_metadata.get("budget_class", "STANDARD")),
            output_form=str(routing_metadata.get("output_form", self._default_output_form(subject))),
            risk_tier=str(routing_metadata.get("risk_tier", "medium")),
            modality=str(routing_metadata.get("modality", "text")),
            local_vs_remote_availability=str(routing_metadata.get("local_vs_remote_availability", "local_first")),
            coding_tool_need=bool(routing_metadata.get("coding_tool_need", False)),
            thinking_vs_nonthinking_need=str(routing_metadata.get("thinking_vs_nonthinking_need", "adaptive")),
            hardware_device_constraints=list(routing_metadata.get("hardware_device_constraints", [])),
            registry_layer_preference=requested_registry_layer,
            allow_remote=bool(routing_metadata.get("allow_remote", False)),
            lineage=lineage,
            benchmark_family=benchmark_family,
            native_takeover_candidate_id=native_takeover_candidate_id,
        )
        decision = self._routing.route(
            context=context,
            assignments=self._assignments,
            profiles={profile.teacher_id: profile for profile in self.list_profiles()},
            active_teacher_id=self._active_teacher_id,
        )
        record = TeacherArbitrationRecord(
            task_type=task_type,
            expert=expert,
            registry_layer=decision.registry_layer,
            candidates=decision.candidates,
            selected_teacher_id=decision.selected_teacher_id,
            selected_teacher_ids=decision.selected_teacher_ids or [decision.selected_teacher_id],
            selected_roles=decision.selected_roles,
            local_vs_remote=self._local_vs_remote(decision.selected_teacher_id),
            reasoning_mode=self._reasoning_mode(decision.selected_teacher_id),
            arbitration_result=self._routing.arbitration_result(decision),
            benchmark_family=benchmark_family,
            teacher_confidence=decision.teacher_confidence,
            dream_lineage=lineage,
            native_takeover_candidate_id=native_takeover_candidate_id,
            rationale=decision.rationale,
            status_label=decision.status_label,
        )
        attached = self._attached.get(decision.selected_teacher_id)
        if attached is None:
            attached = self.attach(
                brain,
                ModelAttachRequest(teacher_id=decision.selected_teacher_id, attach_role="teacher", set_active=True),
                registry_layer=decision.registry_layer,
                routing_decision=decision,
                arbitration=record,
                lineage=lineage,
                benchmark_family=benchmark_family,
                native_takeover_candidate_id=native_takeover_candidate_id,
            )
        self._update_attached_provenance(attached.teacher_id, arbitration=record, routing_decision=decision)
        return self._attached[attached.teacher_id], record

    def retirement_decisions(self, independence: IndependenceMetrics | None = None) -> list[TeacherRetirementDecision]:
        return [
            self._retirement_advisor.evaluate(profile, independence=independence)
            for profile in self.list_profiles()
            if not profile.retired
        ]

    def metadata(self) -> dict:
        return {
            "status_label": self.status_label,
            "schema_version": self.schema_version,
            "migration_notes": self.migration_notes,
            "default_registry_layer": self.default_registry_layer,
            "core_mentor_ensemble": self.core_mentor_ensemble,
            "expert_roster": self.expert_roster,
            "registry_layers": self.registry_layers,
            "routing_policy": {
                "budget_classes": self.routing_policy.get("budget_classes", []),
                "output_forms": self.routing_policy.get("output_forms", []),
                "default_registry_layer": self.routing_policy.get("default_registry_layer"),
                "required_routing_roles": self.routing_policy.get("required_routing_roles", []),
                "lfm2": self.routing_policy.get("lfm2", {}),
            },
            "regimens": {
                "stage_definitions": self.regimens.get("stage_definitions", {}),
                "subjects": sorted(payload.get("subject") for payload in self.regimens.get("expert_regimens", {}).values()),
            },
            "benchmarks": self.benchmark_registry.metadata(),
            "thresholds": self.threshold_registry.metadata(),
            "fleets": self.fleet_registry.metadata(),
            "fleet_windows": self.fleet_window_registry.metadata(),
            "cohort_thresholds": self.cohort_threshold_registry.metadata(),
            "schema_registry": self.schema_registry.metadata(),
            "schema_manifest_path": self.schema_manifest_path,
        }

    def _resolve_profile(self, teacher_id: str | None, model_hint: str | None) -> TeacherProfile | None:
        if teacher_id:
            return self._profiles.get(teacher_id)
        if model_hint:
            for profile in self.list_profiles():
                if model_hint in profile.model_hints:
                    return profile
        return None

    def _hydrate_profile(self, profile: TeacherProfile) -> TeacherProfile:
        available = False
        for model_hint in profile.model_hints:
            try:
                available = self.model_registry.resolve_model(model_hint).available
                if available:
                    break
            except Exception:
                continue
        return profile.model_copy(update={"available": available})

    def _default_registry_layer_for_profile(self, profile: TeacherProfile | None) -> str:
        if profile is None:
            return self.default_registry_layer
        if self.default_registry_layer in profile.registry_layers:
            return self.default_registry_layer
        return profile.registry_layers[0] if profile.registry_layers else self.default_registry_layer

    def _update_attached_provenance(
        self,
        teacher_id: str,
        *,
        arbitration: TeacherArbitrationRecord | None,
        routing_decision: Any | None,
    ) -> None:
        attached = self._attached.get(teacher_id)
        profile = self._profiles.get(teacher_id)
        if attached is None or profile is None:
            return
        provenance = dict(attached.provenance)
        if arbitration is not None:
            provenance["arbitration"] = arbitration.model_dump(mode="json")
            provenance["registry_layer"] = arbitration.registry_layer
            provenance["selected_teachers"] = arbitration.selected_teacher_ids or [arbitration.selected_teacher_id]
            provenance["selected_teacher_roles"] = arbitration.selected_roles
            provenance["arbitration_result"] = arbitration.arbitration_result
            provenance["benchmark_family"] = arbitration.benchmark_family
            if arbitration.benchmark_family and arbitration.expert:
                try:
                    provenance["threshold_set_id"] = self.threshold_registry.resolve(
                        subject=arbitration.expert,
                        benchmark_family=arbitration.benchmark_family,
                    ).threshold_set_id
                except Exception:
                    pass
            provenance["teacher_confidence"] = arbitration.teacher_confidence
            provenance["native_takeover_candidate_id"] = arbitration.native_takeover_candidate_id
        if routing_decision is not None:
            provenance["routing_decision"] = routing_decision.model_dump(mode="json")
        self._attached[teacher_id] = attached.model_copy(update={"provenance": provenance})

    def _default_output_form(self, subject: str) -> str:
        return self.routing_policy.get("domain_defaults", {}).get(subject, {}).get("output_forms", ["SHORT_ANSWER"])[0]

    def _local_vs_remote(self, teacher_id: str) -> str:
        profile = self._profiles.get(teacher_id)
        if not profile or not profile.capability_card:
            return "local"
        locality = profile.capability_card.locality
        if locality == "remote_only":
            return "remote"
        if locality == "mixed_local_then_remote":
            return "mixed"
        return "local"

    def _reasoning_mode(self, teacher_id: str) -> str | None:
        profile = self._profiles.get(teacher_id)
        if not profile or not profile.capability_card or not profile.capability_card.reasoning_modes:
            return None
        return profile.capability_card.reasoning_modes[0]
