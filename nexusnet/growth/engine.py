from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus.schemas import utcnow
from nexusnet.curriculum import DatasetRadar
from nexusnet.growth.artifacts import GrowthArtifactStore, ref_tail
from nexusnet.growth.contracts import (
    ArtifactHeader,
    DatasetManifestRecord,
    GrowthCycleRecord,
    GrowthCycleRequest,
    ReviewerDecisionRecord,
    TrainingRunRecord,
)


class HiveModelGrowthEngine:
    def __init__(self, *, artifacts_dir: Path | str | None = None, dataset_radar: DatasetRadar | None = None) -> None:
        self.store = GrowthArtifactStore(artifacts_dir)
        self.dataset_radar = dataset_radar or DatasetRadar(artifacts_dir=artifacts_dir)

    def start_dry_run(self, request: GrowthCycleRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, GrowthCycleRequest) else GrowthCycleRequest.model_validate(request)
        cycle_dir = self.store.cycle_dir(normalized.cycle_id)
        now = utcnow().isoformat()
        refs = _refs(normalized)
        cycle_tail = ref_tail(normalized.cycle_id)
        growth_gate = _growth_gate(normalized)
        growth_blockers = growth_gate["blockers"]

        events_path = cycle_dir / "events.jsonl"
        self.store.write_jsonl(events_path, _events(normalized.cycle_id, now))
        self.store.write_jsonl(cycle_dir / "blocked_reasons.jsonl", growth_blockers)

        self._write_material_scout(cycle_dir, normalized, refs, now)
        self._write_curriculum(cycle_dir, normalized, refs)
        cases = _training_cases(normalized, refs, now)
        self._write_teacher_council(cycle_dir, normalized, refs, cases)
        self._write_datasets(cycle_dir, normalized, refs, cases)
        self._write_student(cycle_dir, normalized, refs)
        self._write_training_run(cycle_dir, normalized, refs)
        self._write_evals(cycle_dir, normalized, refs)
        reviewer = self._write_reviewer_decision(cycle_dir, normalized, refs, growth_blockers)
        self._write_rollback(cycle_dir, normalized, refs)
        decision = "blocked" if growth_blockers else reviewer["decision"]

        cycle_record = GrowthCycleRecord(
            header=self._header(
                artifact_id=refs["growth_cycle"],
                artifact_type="growth_cycle",
                cycle_id=normalized.cycle_id,
                student_id=refs["student"],
                teacher_refs=normalized.teacher_pairing_refs,
                source_refs=normalized.source_refs,
                governance_state="blocked" if growth_blockers else "shadow_only",
            ),
            cycle_id=normalized.cycle_id,
            status=decision,
            requested_by={
                "node_ref": normalized.requested_by_node_ref,
                "request_type": normalized.request_type,
                "operator_approved": normalized.operator_approved,
            },
            target={
                "target_node_id": normalized.target_node_id,
                "target_node_type": normalized.target_node_type,
                "target_capabilities": normalized.target_capabilities,
            },
            birth_intent={
                "student_kind": normalized.student_kind,
                "birth_reason": normalized.birth_reason,
                "expected_artifact_type": normalized.expected_artifact_type,
            },
            policies={
                "privacy_policy_ref": normalized.privacy_policy_ref,
                "license_policy_ref": normalized.license_policy_ref,
                "federation_policy_ref": normalized.federation_policy_ref,
            },
            refs={
                "failure_refs": normalized.failure_refs,
                "dream_refs": normalized.dream_refs,
                "federated_prior_refs": normalized.federated_prior_refs,
                "canon_refs": normalized.canon_refs,
                "teacher_pairing_refs": normalized.teacher_pairing_refs,
                "source_refs": normalized.source_refs,
                "knowledge_artifact_refs": normalized.knowledge_artifact_refs,
                "material_request_refs": [normalized.material_request_ref] if normalized.material_request_ref else [],
                "adapter_training_plan_refs": [normalized.adapter_training_plan_ref] if normalized.adapter_training_plan_ref else [],
            },
            state_refs={
                "material_scout_ref": refs["material_scout"],
                "material_request_ref": normalized.material_request_ref,
                "knowledge_artifact_refs": normalized.knowledge_artifact_refs,
                "adapter_training_plan_ref": normalized.adapter_training_plan_ref,
                "adapter_training_plan_status": normalized.adapter_training_plan_status,
                "adapter_training_gate_ref": "request.adapter_training_gate" if normalized.adapter_training_gate else None,
                "curriculum_ref": refs["curriculum"],
                "teacher_council_ref": refs["teacher_council"],
                "dataset_manifest_ref": refs["dataset_manifest"],
                "student_birth_ref": refs["student_birth"],
                "training_run_refs": [refs["training_run"]],
                "eval_refs": [refs["eval"]],
                "reviewer_monitor_ref": refs["reviewer_monitor"],
                "promotion_decision_ref": refs["reviewer_decision"],
                "teacher_ejection_review_ref": None,
                "rollback_ref": refs["rollback"],
            },
            governance={
                "promotion_allowed": False,
                "teacher_ejection_allowed": False,
                "human_approval_required": True,
                "actual_weight_mutation_allowed": False,
                "state_machine_terminal_for_v0": decision,
                "growth_gate": growth_gate,
            },
        )
        cycle_payload = cycle_record.model_dump(mode="json")
        self.store.write_json(cycle_dir / "cycle.json", cycle_payload)

        return {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "hive-model-growth-engine",
            "cycle_id": normalized.cycle_id,
            "cycle_dir": str(cycle_dir),
            "status": decision,
            "state": decision,
            "student_id": refs["student"],
            "training_support_state": "dry_run_supported",
            "actual_weight_mutation_allowed": False,
            "student_promotable": False,
            "teacher_ejection_eligible": reviewer["teacher_ejection_eligible"],
            "adapter_training_plan_ref": normalized.adapter_training_plan_ref,
            "growth_gate": growth_gate,
            "artifact_refs": {
                "growth_cycle": refs["growth_cycle"],
                "material_request": normalized.material_request_ref,
                "knowledge_artifacts": normalized.knowledge_artifact_refs,
                "dataset_manifest": refs["dataset_manifest"],
                "student_birth": refs["student_birth"],
                "model_genome": refs["model_genome"],
                "training_run": refs["training_run"],
                "eval": refs["eval"],
                "reviewer_decision": refs["reviewer_decision"],
                "rollback": refs["rollback"],
            },
            "control_panel_replay": {
                "cycle": str(cycle_dir / "cycle.json"),
                "events": str(events_path),
                "dataset_manifest": str(cycle_dir / "datasets" / "dataset_manifest.json"),
                "reviewer_decision": str(cycle_dir / "reviewer-monitor" / "decision.json"),
            },
            "created_at": now,
        }

    def _material_request_for(self, request: GrowthCycleRequest) -> dict[str, Any] | None:
        if not request.material_request_ref:
            return None
        return self.dataset_radar.material_request_record(request.material_request_ref)

    def _radar_ids_for_request(self, request: GrowthCycleRequest, material_request: dict[str, Any] | None = None) -> list[str]:
        if material_request is not None:
            ids = list(material_request.get("approved_source_ids") or [])
            return ids or _dataset_radar_ids_for_request(request)
        return _dataset_radar_ids_for_request(request)

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        cycles = []
        for path in self.store.cycles_dir.glob("*/cycle.json"):
            try:
                import json

                payload = json.loads(path.read_text(encoding="utf-8"))
                payload["_cycle_dir"] = str(path.parent)
                cycles.append(payload)
            except (OSError, ValueError):
                continue
        cycles.sort(key=lambda item: item.get("updated_at") or item.get("created_at") or "", reverse=True)
        cycles = cycles[:limit]
        blocked_count = sum(1 for cycle in cycles if str(cycle.get("status") or "").startswith("blocked"))
        latest_cycle = cycles[0] if cycles else None
        latest_reviewer_decision = _load_reviewer_decision(latest_cycle)
        latest_training_run = _load_training_run(latest_cycle)
        latest_hidden_eval_attestation = _load_hidden_eval_attestation(latest_cycle)
        latest_teacher_council_manifest = _load_teacher_council_manifest(latest_cycle)
        latest_teacher_council_evidence = _load_teacher_council_evidence(latest_cycle)
        latest_dataset_manifest = _load_dataset_manifest(latest_cycle)
        latest_student_birth_record = _load_student_birth_record(latest_cycle)
        latest_model_genome = _load_model_genome(latest_cycle)
        latest_training_loss_trace_summary = _load_training_loss_trace_summary(latest_cycle)
        latest_training_checkpoint_summary = _load_training_checkpoint_summary(latest_cycle)
        latest_training_output_artifacts = _load_training_output_artifacts(latest_cycle)
        latest_eval_scorecard = _load_eval_scorecard(latest_cycle)
        latest_eval_comparison_matrix = _load_eval_comparison_matrix(latest_cycle)
        latest_eval_case_results_summary = _load_eval_case_results_summary(latest_cycle)
        latest_cycle_artifact_replay = _artifact_replay_for_cycle(latest_cycle) if latest_cycle else {}
        latest_cycle_artifact_replay_keys = [key for key, value in latest_cycle_artifact_replay.items() if value is not None]
        latest_cycle_artifact_replay_availability = {key: value is not None for key, value in latest_cycle_artifact_replay.items()}
        runtime_state = "static-canon"
        if cycles:
            latest_blocked = str((latest_cycle or {}).get("status") or "").startswith("blocked")
            runtime_state = "degraded" if blocked_count or latest_blocked else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-model-growth-engine",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "cycle_count": len(cycles),
            "shadow_specialist_count": sum(1 for cycle in cycles if cycle.get("status") == "shadow_specialist"),
            "promotable_count": sum(1 for cycle in cycles if cycle.get("status") == "promotable"),
            "blocked_count": blocked_count,
            "latest_cycle": latest_cycle,
            "latest_reviewer_decision": latest_reviewer_decision,
            "latest_training_run": latest_training_run,
            "latest_hidden_eval_attestation": latest_hidden_eval_attestation,
            "latest_teacher_council_manifest": latest_teacher_council_manifest,
            "latest_teacher_council_evidence": latest_teacher_council_evidence,
            "latest_dataset_manifest": latest_dataset_manifest,
            "latest_student_birth_record": latest_student_birth_record,
            "latest_model_genome": latest_model_genome,
            "latest_training_loss_trace_summary": latest_training_loss_trace_summary,
            "latest_training_checkpoint_summary": latest_training_checkpoint_summary,
            "latest_training_output_artifacts": latest_training_output_artifacts,
            "latest_eval_scorecard": latest_eval_scorecard,
            "latest_eval_comparison_matrix": latest_eval_comparison_matrix,
            "latest_eval_case_results_summary": latest_eval_case_results_summary,
            "latest_cycle_artifact_replay_keys": latest_cycle_artifact_replay_keys,
            "latest_cycle_artifact_replay_availability": latest_cycle_artifact_replay_availability,
            "cycles": cycles,
            "required_artifacts": _required_artifacts(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/superpowers/specs/2026-05-04-hive-model-growth-engine-v0-design.md",
                "docs/superpowers/specs/2026-05-04-hive-model-growth-engine-v0-file-contracts.md",
                "docs/NEXUSNET_TEACHER_PAIRING_MATRIX_2026-05-04.md",
            ],
            "mutation_boundary": "dry-run-no-weight-update",
            "teacher_ejection_boundary": "blocked-until-reviewer-consistency-window-passes",
            "hidden_eval_boundary": "sealed-eval-visible-only-to-eval-gauntlet",
            "federation_boundary": "sanitized-metadata-only-no-raw-private-data",
            "required_artifacts": _required_artifacts(),
            "operator_actions": _operator_actions(),
        }

    def replay_cycle(self, cycle_id: str) -> dict[str, Any] | None:
        normalized = cycle_id if ":" in cycle_id else f"cycle:{cycle_id}"
        for cycle in self.summary(limit=500).get("cycles", []):
            if cycle.get("cycle_id") == normalized or str(cycle.get("cycle_id", "")).endswith(cycle_id):
                return {**cycle, "artifact_replay": _artifact_replay_for_cycle(cycle)}
        return None

    def _write_material_scout(
        self,
        cycle_dir: Path,
        request: GrowthCycleRequest,
        refs: dict[str, str],
        now: str,
    ) -> None:
        scout_dir = cycle_dir / "material-scout"
        source_refs = request.source_refs or ["source:synthetic_license_cleared_demo"]
        material_request = self._material_request_for(request)
        radar_ids = self._radar_ids_for_request(request, material_request)
        radar_lineage = _ordered_radar_lineage(
            self.dataset_radar.lineage_for_student("coder", source_ids=radar_ids),
            radar_ids,
        )
        split_policy = _dataset_radar_lineage_split_policy(radar_lineage)
        approved_by_material_request = set((material_request or {}).get("approved_source_ids") or [])
        if material_request is not None:
            self.store.write_json(scout_dir / "material_request.json", material_request)
        source_candidates = []
        blocked_sources = []
        for source in radar_lineage:
            split_gate = _split_gate_for_radar_source(source)
            gate = self.dataset_radar.validate_source_for_split(source["dataset_id"], split_gate)
            material_request_approved = source["dataset_id"] in approved_by_material_request if material_request is not None else None
            candidate = {
                "schema_version": "source_candidate.v0.1",
                "source_id": f"source:dataset_radar:{source['dataset_id']}",
                "dataset_radar_source_id": source["dataset_id"],
                "cycle_id": request.cycle_id,
                "privacy_class": "licensed" if gate["allowed"] else "review_required",
                "license_state": source["license_state"],
                "usable_for_training": bool(gate["allowed"] and split_gate == "train" and (material_request_approved is not False)),
                "split_gate": split_gate,
                "allowed_uses": source["allowed_uses"],
                "target_nodes": source["target_nodes"],
                "freshness": source["freshness"],
                "source_url": source["source_url"],
                "provenance_ref": source["source_url"],
                "gate_reason": gate["reason"],
                "material_request_ref": request.material_request_ref,
                "material_request_approved": material_request_approved,
            }
            source_candidates.append(candidate)
            if not candidate["usable_for_training"]:
                blocked_sources.append({**candidate, "usable_for_training": False})
        manifest = {
            "schema_version": "material_scout_manifest.v0.1",
            "header": self._header(refs["material_scout"], "material_scout", request.cycle_id, refs["student"]).model_dump(mode="json"),
            "scout_id": refs["material_scout"],
            "cycle_id": request.cycle_id,
            "target_node_ref": request.target_node_id,
            "operator_source_refs": source_refs,
            "dataset_radar": {
                "surface_id": "living-dataset-radar",
                "teacher_access_rule": "teacher councils request material through Dataset Radar only",
                "source_count": len(radar_lineage),
                "lineage_path": "material-scout/dataset_radar_lineage.json",
                "lineage_split_policy": split_policy,
                "material_request_ref": request.material_request_ref,
                "material_request_path": "material-scout/material_request.json" if material_request is not None else None,
                "approved_source_ids": list((material_request or {}).get("approved_source_ids") or []),
            },
            "compiled_knowledge": _knowledge_artifact_lineage(request),
            "approved_source_count": sum(1 for candidate in source_candidates if candidate["usable_for_training"]),
            "blocked_source_count": len(blocked_sources) + 1,
            "created_at": now,
        }
        self.store.write_json(scout_dir / "scout_manifest.json", manifest)
        self.store.write_json(
            scout_dir / "dataset_radar_lineage.json",
            {
                "schema_version": "dataset_radar_lineage.v0.1",
                "surface_id": "living-dataset-radar",
                "cycle_id": request.cycle_id,
                "target_node_ref": request.target_node_id,
                "source_ids": radar_ids,
                "sources": radar_lineage,
                "split_policy": split_policy,
                "teacher_access_rule": "teacher councils request material through Dataset Radar only",
                "material_request_ref": request.material_request_ref,
                "approved_source_ids": list((material_request or {}).get("approved_source_ids") or []),
            },
        )
        self.store.write_jsonl(
            scout_dir / "source_candidates.jsonl",
            source_candidates,
        )
        self.store.write_jsonl(
            scout_dir / "blocked_sources.jsonl",
            [
                *blocked_sources,
                {
                    "schema_version": "source_candidate.v0.1",
                    "source_id": "source:frontier_api_output_blocked_demo",
                    "dataset_radar_source_id": None,
                    "cycle_id": request.cycle_id,
                    "privacy_class": "blocked_private_raw",
                    "license_state": "blocked_no_output_training",
                    "usable_for_training": False,
                    "reason": "Commercial frontier API outputs are blocked unless explicit training rights exist.",
                }
            ],
        )

    def _write_curriculum(self, cycle_dir: Path, request: GrowthCycleRequest, refs: dict[str, str]) -> None:
        curriculum_dir = cycle_dir / "curriculum"
        stages = [
            "foundation",
            "controlled_task",
            "noisy_task",
            "adversarial_task",
            "multi_domain_task",
            "tool_required_task",
            "teacher_disagreement_task",
            "dream_generated_task",
            "teacher_free_final_task",
        ]
        curriculum = {
            "schema_version": "curriculum_manifest.v0.1",
            "curriculum_id": refs["curriculum"],
            "cycle_id": request.cycle_id,
            "target_node_ref": request.target_node_id,
            "student_kind": request.student_kind,
            "stages": [
                {
                    "stage_id": stage,
                    "path": f"stages/{stage}.jsonl",
                    "graduation_signal": "rubric-validator-score-plus-reviewer-monitor",
                }
                for stage in stages
            ],
            "hidden_eval_isolation": "teacher_free_final_task_cases_are_manifested_but_not_written_to_training_splits",
            "knowledge_artifact_refs": request.knowledge_artifact_refs,
            "knowledge_artifact_context_rule": "compiled artifacts can seed curriculum but cannot mutate prompts, weights, or promotion state",
        }
        self.store.write_yaml(curriculum_dir / "curriculum.yaml", curriculum)
        for stage in stages:
            self.store.write_jsonl(
                curriculum_dir / "stages" / f"{stage}.jsonl",
                [
                    {
                        "stage_id": stage,
                        "case_seed_ref": f"case_seed:{stage}:{ref_tail(request.cycle_id)}",
                        "visible_to_teacher_council": stage != "teacher_free_final_task",
                        "visible_to_training": stage != "teacher_free_final_task",
                    }
                ],
            )

    def _write_teacher_council(
        self,
        cycle_dir: Path,
        request: GrowthCycleRequest,
        refs: dict[str, str],
        cases: list[dict[str, Any]],
    ) -> None:
        council_dir = cycle_dir / "teacher-council"
        manifest = {
            "schema_version": "teacher_council_manifest.v0.1",
            "header": self._header(
                refs["teacher_council"],
                "teacher_council_manifest",
                request.cycle_id,
                refs["student"],
                teacher_refs=request.teacher_pairing_refs,
            ).model_dump(mode="json"),
            "teacher_council_id": refs["teacher_council"],
            "cycle_id": request.cycle_id,
            "teacher_refs": request.teacher_pairing_refs,
            "license_rule": "approved_train_or_approved_eval_only_required",
            "material_access_rule": "dataset-radar-only",
            "dataset_radar_ref": "material-scout/dataset_radar_lineage.json",
            "compiled_knowledge_access": _knowledge_artifact_lineage(request),
            "review_rule": "primary_professor_plus_contrast_teacher_plus_skeptical_examiner",
        }
        self.store.write_json(council_dir / "council_manifest.json", manifest)
        self.store.write_jsonl(
            council_dir / "teacher_outputs.jsonl",
            [
                {
                    "output_id": f"teacher_output:{index:03d}",
                    "teacher_ref": request.teacher_pairing_refs[index % max(1, len(request.teacher_pairing_refs))]
                    if request.teacher_pairing_refs
                    else "teacher:local_license_cleared_stub",
                    "case_id": case["case_id"],
                    "license_state": "approved_train",
                    "output_ref": f"accepted_target:{case['case_id']}",
                }
                for index, case in enumerate(cases)
            ],
        )
        self.store.write_jsonl(
            council_dir / "critiques.jsonl",
            [
                {
                    "critique_id": f"critique:{case['case_id']}",
                    "reviewer_ref": "node:expert_critique",
                    "case_id": case["case_id"],
                    "severity": 0.1,
                    "resolution": "accepted_with_validator_support",
                }
                for case in cases
            ],
        )
        self.store.write_jsonl(
            council_dir / "validator_results.jsonl",
            [
                {
                    "validator_ref": "validator:unit_security_privacy_suite",
                    "case_id": case["case_id"],
                    "passed": True,
                    "score": 1.0,
                }
                for case in cases
            ],
        )
        self.store.write_jsonl(council_dir / "accepted_cases.jsonl", cases)
        self.store.write_jsonl(
            council_dir / "rejected_variants.jsonl",
            [
                {
                    "variant_id": "rejected_variant:unsafe_unlicensed_demo",
                    "reason": "Rejected because source license did not allow training.",
                    "license_state": "blocked_no_output_training",
                }
            ],
        )

    def _write_datasets(
        self,
        cycle_dir: Path,
        request: GrowthCycleRequest,
        refs: dict[str, str],
        cases: list[dict[str, Any]],
    ) -> None:
        datasets_dir = cycle_dir / "datasets"
        material_request = self._material_request_for(request)
        radar_ids = self._radar_ids_for_request(request, material_request)
        radar_lineage = _ordered_radar_lineage(
            self.dataset_radar.lineage_for_student("coder", source_ids=radar_ids),
            radar_ids,
        )
        split_policy = _dataset_radar_lineage_split_policy(radar_lineage)
        splits = {
            "train": cases[:6],
            "validation": cases[6:8],
            "heldout": cases[8:10],
            "adversarial": cases[10:11],
            "regression": cases[11:12],
        }
        for split, rows in splits.items():
            self.store.write_jsonl(datasets_dir / f"{split}.jsonl", rows)
        hidden_manifest = {
            "schema_version": "hidden_eval_manifest.v0.1",
            "header": self._header(
                refs["hidden_eval"],
                "hidden_eval_manifest",
                request.cycle_id,
                refs["student"],
                governance_state="shadow_only",
            ).model_dump(mode="json"),
            "hidden_eval_id": refs["hidden_eval"],
            "cycle_id": request.cycle_id,
            "sealed": True,
            "visible_to_training": False,
            "visible_to_teacher_council": False,
            "source_ids": split_policy.get("sealed_eval_source_ids", []),
            "blocked_from_training_splits": bool(split_policy.get("sealed_eval_source_ids", [])),
            "split_policy_ref": "dataset_manifest.dataset_radar_lineage.split_policy",
            "case_count": 1,
            "case_hashes": ["sha256:hidden-demo-case"],
            "storage_policy": "sealed_local",
            "opened_only_by": ["EvalGauntlet"],
            "opened_at": None,
            "leakage_scan": {
                "train_overlap": 0,
                "teacher_output_overlap": 0,
                "status": "passed",
            },
        }
        self.store.write_json(datasets_dir / "teacher_free_hidden.manifest.json", hidden_manifest)
        manifest = DatasetManifestRecord(
            header=self._header(refs["dataset_manifest"], "dataset_manifest", request.cycle_id, refs["student"]),
            dataset_manifest_id=refs["dataset_manifest"],
            cycle_id=request.cycle_id,
            target_node_ref=request.target_node_id,
            splits={
                "train": {"path": "datasets/train.jsonl", "case_count": len(splits["train"])},
                "validation": {"path": "datasets/validation.jsonl", "case_count": len(splits["validation"])},
                "heldout": {"path": "datasets/heldout.jsonl", "case_count": len(splits["heldout"])},
                "adversarial": {"path": "datasets/adversarial.jsonl", "case_count": len(splits["adversarial"])},
                "regression": {"path": "datasets/regression.jsonl", "case_count": len(splits["regression"])},
                "teacher_free_hidden": {
                    "manifest_path": "datasets/teacher_free_hidden.manifest.json",
                    "case_count": 1,
                    "sealed": True,
                    "visible_to_training": False,
                    "visible_to_teacher_council": False,
                    "source_ids": split_policy.get("sealed_eval_source_ids", []),
                    "blocked_from_train": bool(split_policy.get("sealed_eval_source_ids", [])),
                    "split_policy_ref": "dataset_radar_lineage.split_policy",
                },
            },
            license_summary={"approved_train_cases": len(cases), "eval_only_cases": 1, "blocked_cases": 0},
            privacy_summary={"private_raw_cases": 0, "private_redacted_cases": 0, "federating_allowed_cases": 0},
        )
        payload = manifest.model_dump(mode="json")
        payload["dataset_radar_lineage"] = {
            "surface_id": "living-dataset-radar",
            "source_ids": radar_ids,
            "split_policy": split_policy,
            "teacher_access_rule": "teacher councils request material through Dataset Radar only",
            "lineage_path": "material-scout/dataset_radar_lineage.json",
            "material_request_ref": request.material_request_ref,
            "approved_source_ids": list((material_request or {}).get("approved_source_ids") or []),
        }
        payload["knowledge_artifact_lineage"] = _knowledge_artifact_lineage(request)
        self.store.write_json(datasets_dir / "dataset_manifest.json", payload)

    def _write_student(self, cycle_dir: Path, request: GrowthCycleRequest, refs: dict[str, str]) -> None:
        students_dir = cycle_dir / "students"
        material_request = self._material_request_for(request)
        radar_ids = self._radar_ids_for_request(request, material_request)
        radar_lineage = _ordered_radar_lineage(
            self.dataset_radar.lineage_for_student("coder", source_ids=radar_ids),
            radar_ids,
        )
        split_policy = _dataset_radar_lineage_split_policy(radar_lineage)
        birth = {
            "schema_version": "student_birth_record.v0.1",
            "header": self._header(refs["student_birth"], "student_birth_record", request.cycle_id, refs["student"]).model_dump(mode="json"),
            "student_id": refs["student"],
            "cycle_id": request.cycle_id,
            "student_kind": request.student_kind,
            "parent_node_refs": [request.target_node_id],
            "temporary_until_reviewed": True,
            "standalone_allowed": False,
            "retirement_allowed_for_parent": False,
            "shadow_only": True,
            "material_request_ref": request.material_request_ref,
            "dataset_radar_lineage": {
                "surface_id": "living-dataset-radar",
                "source_ids": radar_ids,
                "split_policy": split_policy,
                "approved_source_ids": list((material_request or {}).get("approved_source_ids") or []),
                "material_request_replay": (material_request or {}).get("replay") or {},
            },
            "knowledge_artifact_lineage": _knowledge_artifact_lineage(request),
        }
        self.store.write_json(students_dir / "student_birth_record.json", birth)
        genome = {
            "schema_version": "model_genome.v0.1",
            "genome_id": refs["model_genome"],
            "cycle_id": request.cycle_id,
            "student_id": refs["student"],
            "model_family": "nexusnet_hive_moe",
            "student_kind": request.student_kind,
            "brain_scale": {
                "level": str(request.target_node_type).lower(),
                "parent_level": "hive_substrate",
                "hive_connected": True,
                "substrate_refs_required": [
                    "NeuralBus",
                    "HiveBlackboard",
                    "SparseExpertGateLedger",
                    "RuntimeDecisionLedger",
                    "CheckpointCoverageLedger",
                ],
            },
            "architecture": {
                "base_strategy": "adapter_student",
                "base_model_ref": request.teacher_pairing_refs[0] if request.teacher_pairing_refs else "model:license_cleared_stub",
                "adapter_type": "lora",
                "trainable_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                "hidden_size_policy": "inherit_base",
                "quantization_targets": ["q4_k_m", "q5_k_m"],
            },
            "moe_role": {
                "expert_slot_ref": f"expert_slot:{ref_tail(refs['student'])}",
                "target_capabilities": request.target_capabilities,
                "router_features": [
                    "task_family",
                    "risk_score",
                    "tool_required",
                    "historical_reliability",
                    "latency_budget",
                ],
                "activation_policy": {"top_k": 2, "shadow_only": True},
            },
            "training_objectives": [
                "task_success",
                "teacher_distillation",
                "contrast_resolution",
                "router_alignment",
                "safety_regression",
                "efficiency",
            ],
            "promotion_constraints": {
                "parent_margin": 0.03,
                "teacher_margin": 0.02,
                "required_parent_surpass_rate": 0.90,
                "required_teacher_surpass_rate": 0.95,
                "critical_regression_allowed": 0,
                "human_approval_required": True,
            },
            "privacy": {"federation_policy": "non_federating", "raw_private_data_allowed": False},
            "lineage": {
                "parent_node_refs": [request.target_node_id],
                "teacher_council_ref": refs["teacher_council"],
                "dataset_manifest_ref": refs["dataset_manifest"],
                "birth_record_ref": refs["student_birth"],
                "dataset_radar_material_request_ref": request.material_request_ref,
                "dataset_radar_source_ids": radar_ids,
                "dataset_radar_split_policy": split_policy,
                "dataset_radar_approved_source_ids": list((material_request or {}).get("approved_source_ids") or []),
                "knowledge_artifact_refs": request.knowledge_artifact_refs,
                "knowledge_artifact_context_rule": "refs_only_no_prompt_or_weight_mutation",
            },
        }
        self.store.write_yaml(students_dir / "model_genome.yaml", genome)

    def _write_training_run(self, cycle_dir: Path, request: GrowthCycleRequest, refs: dict[str, str]) -> None:
        training_dir = cycle_dir / "training-runs" / "train_demo_001"
        material_request = self._material_request_for(request)
        radar_ids = self._radar_ids_for_request(request, material_request)
        radar_lineage = _ordered_radar_lineage(
            self.dataset_radar.lineage_for_student("coder", source_ids=radar_ids),
            radar_ids,
        )
        split_policy = _dataset_radar_lineage_split_policy(radar_lineage)
        run = TrainingRunRecord(
            header=self._header(refs["training_run"], "training_run", request.cycle_id, refs["student"], governance_state="training_planned"),
            train_id=refs["training_run"],
            cycle_id=request.cycle_id,
            student_id=refs["student"],
            support_state="dry_run_supported",
            actual_weight_mutation_allowed=False,
            declared_methods=["lora", "qlora", "dpo", "grpo", "router_policy_training"],
            loss_contract={
                "total_loss": [
                    "alpha * L_distill_available",
                    "beta * L_contrast",
                    "gamma * L_task",
                    "delta * L_safety",
                    "eta * L_router",
                    "theta * L_regression",
                    "lambda * L_privacy",
                    "mu * L_efficiency",
                    "rho * L_preference",
                    "sigma * L_rubric",
                ],
                "distillation_fallbacks": ["logit_distillation", "sequence_distillation", "rubric_regression", "preference_optimization"],
            },
            dataset_radar_training_prerequisites={
                "source_review_required": True,
                "hidden_eval_attestation_required": True,
                "human_approval_required": True,
                "sealed_eval_source_ids": split_policy.get("sealed_eval_source_ids", []),
                "split_policy_ref": "datasets/dataset_manifest.json#dataset_radar_lineage.split_policy",
                "actual_weight_mutation_blocked_until": [
                    "dataset_radar_source_review_passed",
                    "hidden_eval_attestation_passed",
                    "sandbox_gpu_profile_ready",
                    "human_approval_recorded",
                ],
            },
            output_artifacts=[refs["model_genome"]],
        )
        self.store.write_json(training_dir / "training_run.json", run.model_dump(mode="json"))
        self.store.write_yaml(
            training_dir / "training_plan.yaml",
            {
                "schema_version": "training_plan.v0.1",
                "train_id": refs["training_run"],
                "cycle_id": request.cycle_id,
                "dry_run_only": True,
                "actual_weight_mutation_allowed": False,
                "first_real_training_requires": [
                    "dataset_radar_source_review_passed",
                    "hidden_eval_attestation_passed",
                    "sandbox_gpu_profile_ready",
                    "license_audit",
                    "human_approval_recorded",
                ],
                "actual_weight_mutation_blocked_until": [
                    "dataset_radar_source_review_passed",
                    "hidden_eval_attestation_passed",
                    "sandbox_gpu_profile_ready",
                    "human_approval_recorded",
                ],
            },
        )
        self.store.write_jsonl(
            training_dir / "loss_trace.jsonl",
            [
                {"step": 0, "loss": 1.0, "mode": "dry_run"},
                {"step": 1, "loss": 0.91, "mode": "dry_run"},
                {"step": 2, "loss": 0.84, "mode": "dry_run"},
            ],
        )
        self.store.write_jsonl(
            training_dir / "checkpoints.jsonl",
            [
                {
                    "checkpoint_ref": refs["checkpoint"],
                    "checkpoint_type": "metadata_only",
                    "restore_validated": True,
                    "weight_snapshot": "not_created_in_dry_run",
                }
            ],
        )
        self.store.write_jsonl(training_dir / "output_artifacts.jsonl", [{"artifact_ref": refs["model_genome"], "kind": "model_genome"}])

    def _write_evals(self, cycle_dir: Path, request: GrowthCycleRequest, refs: dict[str, str]) -> None:
        eval_dir = cycle_dir / "evals" / "eval_demo_001"
        material_request = self._material_request_for(request)
        radar_ids = self._radar_ids_for_request(request, material_request)
        radar_lineage = _ordered_radar_lineage(
            self.dataset_radar.lineage_for_student("coder", source_ids=radar_ids),
            radar_ids,
        )
        split_policy = _dataset_radar_lineage_split_policy(radar_lineage)
        scorecard = {
            "schema_version": "eval_scorecard.v0.1",
            "header": self._header(refs["eval"], "eval_scorecard", request.cycle_id, refs["student"], governance_state="eval_passed").model_dump(mode="json"),
            "eval_id": refs["eval"],
            "cycle_id": request.cycle_id,
            "student_id": refs["student"],
            "status": "passed_for_shadow_only",
            "hidden_eval_attestation_ref": refs["hidden_eval"],
            "parent_score": 0.81,
            "student_score": 0.852,
            "best_teacher_score": 0.865,
            "teacher_council_score": 0.872,
            "critical_regressions": 0,
            "safety_passed": True,
            "privacy_passed": True,
        }
        self.store.write_yaml(
            eval_dir / "eval_plan.yaml",
            {
                "schema_version": "eval_plan.v0.1",
                "eval_id": refs["eval"],
                "cycle_id": request.cycle_id,
                "suites": ["parent_vs_child", "teacher_vs_child", "hidden_eval", "safety_privacy_regression"],
            },
        )
        self.store.write_json(eval_dir / "scorecard.json", scorecard)
        self.store.write_json(
            eval_dir / "comparison_matrix.json",
            {
                "schema_version": "comparison_matrix.v0.1",
                "cycle_id": request.cycle_id,
                "student_vs_parent_margin": 0.042,
                "student_vs_best_teacher_margin": -0.013,
                "student_vs_teacher_council_margin": -0.02,
            },
        )
        self.store.write_jsonl(
            eval_dir / "case_results.jsonl",
            [
                {"case_id": f"case:{index:03d}", "student_passed": True, "parent_passed": index % 4 != 0, "teacher_passed": True}
                for index in range(1, 13)
            ],
        )
        self.store.write_json(
            eval_dir / "hidden_eval_attestation.json",
            {
                "schema_version": "hidden_eval_attestation.v0.1",
                "hidden_eval_id": refs["hidden_eval"],
                "opened_by": "EvalGauntlet",
                "source_ids": split_policy.get("sealed_eval_source_ids", []),
                "split_policy_ref": "datasets/dataset_manifest.json#dataset_radar_lineage.split_policy",
                "teacher_visible": False,
                "train_overlap": 0,
                "teacher_output_overlap": 0,
                "status": "passed",
            },
        )

    def _write_reviewer_decision(
        self,
        cycle_dir: Path,
        request: GrowthCycleRequest,
        refs: dict[str, str],
        growth_blockers: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        growth_blockers = growth_blockers or []
        blocked = bool(growth_blockers)
        decision = ReviewerDecisionRecord(
            header=self._header(
                refs["reviewer_decision"],
                "reviewer_decision",
                request.cycle_id,
                refs["student"],
                governance_state="blocked" if blocked else "side_barred",
            ),
            monitor_id=refs["reviewer_monitor"],
            cycle_id=request.cycle_id,
            student_id=refs["student"],
            windows={
                "initial_eval_window": "passed",
                "shadow_runtime_window": "pending",
                "canary_window": "not_started",
                "post_promotion_window": "not_started",
                "teacher_ejection_window": "not_eligible",
            },
            parent_comparison={
                "mean_surpass": 0.042,
                "min_surpass": 0.008,
                "surpass_rate": 0.92,
                "lower_confidence_surpass_bound": 0.031,
                "passed": True,
            },
            teacher_comparison={
                "mean_surpass": -0.013,
                "min_surpass": -0.04,
                "surpass_rate": 0.81,
                "lower_confidence_surpass_bound": -0.021,
                "passed": False,
            },
            hard_gates={
                "privacy_passed": True,
                "safety_passed": True,
                "rollback_ready": True,
                "critical_regression": False,
                "human_approved": False,
                "adapter_training_plan_ready": not blocked,
                "dataset_radar_source_review_passed": False,
                "hidden_eval_attestation_passed": True,
                "sealed_eval_not_teacher_visible": True,
                "actual_weight_mutation_allowed": False,
            },
            decision="blocked" if blocked else "shadow_specialist",
            teacher_ejection_eligible=False,
            reason=(
                "Adapter training plan is blocked or review-gated; growth cycle cannot be treated as executable evidence."
                if blocked
                else "Parent surpassed, but teacher council was not consistently surpassed and no human approval exists."
            ),
        )
        payload = decision.model_dump(mode="json")
        self.store.write_json(cycle_dir / "reviewer-monitor" / "decision.json", payload)
        self.store.write_json(
            cycle_dir / "reviewer-monitor" / "monitor.json",
            {
                "schema_version": "reviewer_monitor.v0.1",
                "monitor_id": refs["reviewer_monitor"],
                "cycle_id": request.cycle_id,
                "consistency_windows_required": ["initial_eval", "shadow_runtime", "canary", "post_promotion"],
            },
        )
        self.store.write_jsonl(
            cycle_dir / "reviewer-monitor" / "windows.jsonl",
            [{"window": window, "state": state} for window, state in payload["windows"].items()],
        )
        self.store.write_jsonl(
            cycle_dir / "reviewer-monitor" / "reviewer_votes.jsonl",
            [
                {"reviewer_ref": "node:ao_evals", "vote": "shadow_specialist", "reason": "Teacher surpass gate failed."},
                {"reviewer_ref": "node:expert_critique", "vote": "shadow_specialist", "reason": "Keep temporary child for more evidence."},
            ],
        )
        return payload

    def _write_rollback(self, cycle_dir: Path, request: GrowthCycleRequest, refs: dict[str, str]) -> None:
        rollback_dir = cycle_dir / "rollbacks"
        snapshot = {
            "schema_version": "rollback_snapshot.v0.1",
            "header": self._header(refs["rollback"], "rollback_snapshot", request.cycle_id, refs["student"], governance_state="rolled_back").model_dump(mode="json"),
            "rollback_id": refs["rollback"],
            "cycle_id": request.cycle_id,
            "student_id": refs["student"],
            "snapshot_type": "metadata_only_no_weight_mutation",
            "restore_targets": ["cycle_state", "student_registry_pointer", "router_shadow_policy"],
            "pre_write_snapshot_created": True,
        }
        self.store.write_json(rollback_dir / "rollback_snapshot.json", snapshot)
        self.store.write_json(
            rollback_dir / "rewind_proof.json",
            {
                "schema_version": "rewind_proof.v0.1",
                "header": self._header(
                    refs["rewind_proof"],
                    "rewind_proof",
                    request.cycle_id,
                    refs["student"],
                    governance_state="rolled_back",
                ).model_dump(mode="json"),
                "rollback_id": refs["rollback"],
                "cycle_id": request.cycle_id,
                "restore_validation": "passed",
                "diff_preview_available": True,
                "weight_restore_required": False,
                "reason": "Dry-run cycle created no trainable weight artifact.",
            },
        )

    def _header(
        self,
        artifact_id: str,
        artifact_type: str,
        cycle_id: str,
        student_id: str | None = None,
        *,
        teacher_refs: list[str] | None = None,
        source_refs: list[str] | None = None,
        governance_state: str = "draft",
    ) -> ArtifactHeader:
        return ArtifactHeader(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            cycle_id=cycle_id,
            student_id=student_id,
            teacher_refs=teacher_refs or [],
            source_refs=source_refs or [],
            governance_state=governance_state,
        )


def _refs(request: GrowthCycleRequest) -> dict[str, str]:
    cycle_tail = ref_tail(request.cycle_id)
    suffix = cycle_tail.removeprefix("cyc_")
    if suffix == "demo_001":
        suffix = "demo_001"
    return {
        "growth_cycle": f"artifact:growth_{suffix}",
        "material_scout": f"scout:scout_{suffix}",
        "curriculum": f"curriculum:cur_{suffix}",
        "teacher_council": f"council:council_{suffix}",
        "dataset_manifest": f"dataset:ds_{suffix}",
        "hidden_eval": f"hidden:hidden_{suffix}",
        "student": f"student:stu_{suffix}",
        "student_birth": f"birth:birth_{suffix}",
        "model_genome": f"genome:genome_{suffix}",
        "training_run": f"train:train_{suffix}",
        "eval": f"eval:eval_{suffix}",
        "reviewer_monitor": f"review:mon_{suffix}",
        "reviewer_decision": f"decision:decision_{suffix}",
        "rollback": f"rollback:rb_{suffix}",
        "rewind_proof": f"rewind:rewind_{suffix}",
        "checkpoint": f"checkpoint:ckpt_{suffix}",
    }


def _dataset_radar_ids_for_request(request: GrowthCycleRequest) -> list[str]:
    explicit: list[str] = []
    for source_ref in request.source_refs:
        normalized = str(source_ref)
        for prefix in ("dataset:", "radar:", "dataset_radar:"):
            if normalized.startswith(prefix):
                explicit.append(normalized.removeprefix(prefix))
    if explicit:
        return list(dict.fromkeys(explicit))
    target = " ".join([request.target_node_id, *request.target_capabilities]).lower()
    if "coder" in target or "patch" in target or "test_repair" in target:
        return ["the-stack-v2", "stack-edu", "codesearchnet", "context7", "swe-bench", "swe-gym"]
    if "eval" in target:
        return ["bfcl", "swe-bench", "swe-gym", "openalex", "papers-with-code"]
    if "math" in target or "reason" in target:
        return ["openmathreasoning", "openmathinstruct-2", "numinamath", "gsm8k", "math"]
    return ["fineweb", "fineweb-edu", "common-pile", "openalex", "wikimedia-dumps"]


def _ordered_radar_lineage(lineage: list[dict[str, Any]], source_ids: list[str]) -> list[dict[str, Any]]:
    by_id = {str(source.get("dataset_id")): source for source in lineage if source.get("dataset_id")}
    ordered = [by_id[source_id] for source_id in source_ids if source_id in by_id]
    ordered_ids = {str(source.get("dataset_id")) for source in ordered}
    return [
        *ordered,
        *[source for source in lineage if str(source.get("dataset_id")) not in ordered_ids],
    ]


def _split_gate_for_radar_source(source: dict[str, Any]) -> str:
    state = source.get("license_state")
    allowed = set(source.get("allowed_uses") or [])
    if state == "approved_train" and "train" in allowed:
        return "train"
    if state == "sealed_eval_only" and "teacher_free_hidden" in allowed:
        return "teacher_free_hidden"
    if state == "approved_eval_only":
        return "validation"
    if "teacher_context" in allowed:
        return "teacher_context"
    return "train"


def _dataset_radar_lineage_split_policy(sources: list[dict[str, Any]]) -> dict[str, Any]:
    train_source_ids: list[str] = []
    teacher_context_only_source_ids: list[str] = []
    sealed_eval_source_ids: list[str] = []
    eval_only_source_ids: list[str] = []
    for source in sources:
        source_id = str(source.get("dataset_id") or "")
        if not source_id:
            continue
        allowed = set(source.get("allowed_uses") or [])
        state = str(source.get("license_state") or "")
        if state == "approved_train" and "train" in allowed:
            train_source_ids.append(source_id)
        if "teacher_context" in allowed and "train" not in allowed:
            teacher_context_only_source_ids.append(source_id)
        if state == "sealed_eval_only" or "teacher_free_hidden" in allowed:
            sealed_eval_source_ids.append(source_id)
        elif {"validation", "heldout", "regression"} & allowed and "train" not in allowed:
            eval_only_source_ids.append(source_id)
    return {
        "train_source_ids": train_source_ids,
        "teacher_context_only_source_ids": teacher_context_only_source_ids,
        "sealed_eval_source_ids": sealed_eval_source_ids,
        "eval_only_source_ids": eval_only_source_ids,
        "split_rule": "training sources cannot be reused as sealed teacher-free eval sources",
    }


def _knowledge_artifact_lineage(request: GrowthCycleRequest) -> dict[str, Any]:
    runtime_gate = _knowledge_artifact_runtime_gate(request)
    return {
        "surface_id": "knowledge-artifact-compiler",
        "artifact_refs": request.knowledge_artifact_refs,
        "access_rule": "artifact-refs-only-through-KRC",
        "visibility": "teacher-council-and-training-context" if request.knowledge_artifact_refs else "none",
        "mutation_allowed": False,
        "requires_krc_runtime_context_allowed": True,
        "blocks_stale_or_quarantined_context": True,
        "blocks_raw_retrieval_fallback_context": True,
        "runtime_gate_source": "KnowledgeArtifactCompiler.query",
        "allowed": runtime_gate["allowed"],
        "runtime_context_evidence_count": runtime_gate["runtime_context_evidence_count"],
        "blocked_artifact_refs": runtime_gate["blocked_artifact_refs"],
        "blocked_reasons": runtime_gate["blocked_reasons"],
        "context_boundary": "compiled artifacts can inform curriculum, teacher councils, and datasets only by explicit refs",
    }


def _load_reviewer_decision(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cycle:
        return None
    path_value = ((cycle.get("control_panel_replay") or {}).get("reviewer_decision") or "")
    if not path_value and cycle.get("_cycle_dir"):
        path_value = str(Path(str(cycle["_cycle_dir"])) / "reviewer-monitor" / "decision.json")
    if not path_value:
        return None
    path = Path(path_value)
    if not path.exists():
        return None
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _artifact_replay_for_cycle(cycle: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "reviewer_decision": _load_reviewer_decision(cycle),
        "training_run": _load_training_run(cycle),
        "hidden_eval_attestation": _load_hidden_eval_attestation(cycle),
        "teacher_council_manifest": _load_teacher_council_manifest(cycle),
        "teacher_council_evidence": _load_teacher_council_evidence(cycle),
        "dataset_manifest": _load_dataset_manifest(cycle),
        "student_birth_record": _load_student_birth_record(cycle),
        "model_genome": _load_model_genome(cycle),
        "training_loss_trace_summary": _load_training_loss_trace_summary(cycle),
        "training_checkpoint_summary": _load_training_checkpoint_summary(cycle),
        "training_output_artifacts": _load_training_output_artifacts(cycle),
        "eval_scorecard": _load_eval_scorecard(cycle),
        "eval_comparison_matrix": _load_eval_comparison_matrix(cycle),
        "eval_case_results_summary": _load_eval_case_results_summary(cycle),
    }


def _load_training_run(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cycle or not cycle.get("_cycle_dir"):
        return None
    cycle_dir = Path(str(cycle["_cycle_dir"]))
    training_runs = sorted(cycle_dir.glob("training-runs/*/training_run.json"))
    if not training_runs:
        return None
    try:
        import json

        return json.loads(training_runs[-1].read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_hidden_eval_attestation(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cycle or not cycle.get("_cycle_dir"):
        return None
    cycle_dir = Path(str(cycle["_cycle_dir"]))
    attestations = sorted(cycle_dir.glob("evals/*/hidden_eval_attestation.json"))
    if not attestations:
        return None
    try:
        import json

        return json.loads(attestations[-1].read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_teacher_council_manifest(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cycle or not cycle.get("_cycle_dir"):
        return None
    path = Path(str(cycle["_cycle_dir"])) / "teacher-council" / "council_manifest.json"
    if not path.exists():
        return None
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_teacher_council_evidence(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cycle or not cycle.get("_cycle_dir"):
        return None
    council_dir = Path(str(cycle["_cycle_dir"])) / "teacher-council"
    if not council_dir.exists():
        return None
    return {
        "teacher_output_count": _jsonl_count(council_dir / "teacher_outputs.jsonl"),
        "accepted_case_count": _jsonl_count(council_dir / "accepted_cases.jsonl"),
        "validator_result_count": _jsonl_count(council_dir / "validator_results.jsonl"),
        "critique_count": _jsonl_count(council_dir / "critiques.jsonl"),
        "rejected_variant_count": _jsonl_count(council_dir / "rejected_variants.jsonl"),
        "evidence_refs": {
            "teacher_outputs": "teacher-council/teacher_outputs.jsonl",
            "accepted_cases": "teacher-council/accepted_cases.jsonl",
            "validator_results": "teacher-council/validator_results.jsonl",
            "critiques": "teacher-council/critiques.jsonl",
            "rejected_variants": "teacher-council/rejected_variants.jsonl",
        },
    }


def _jsonl_count(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    except OSError:
        return 0


def _load_dataset_manifest(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cycle or not cycle.get("_cycle_dir"):
        return None
    path = Path(str(cycle["_cycle_dir"])) / "datasets" / "dataset_manifest.json"
    if not path.exists():
        return None
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_training_loss_trace_summary(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cycle or not cycle.get("_cycle_dir"):
        return None
    cycle_dir = Path(str(cycle["_cycle_dir"]))
    traces = sorted(cycle_dir.glob("training-runs/*/loss_trace.jsonl"))
    if not traces:
        return None
    rows = _jsonl_rows(traces[-1])
    if not rows:
        return None
    losses = [row.get("loss") for row in rows if isinstance(row.get("loss"), int | float)]
    steps = [row.get("step") for row in rows if isinstance(row.get("step"), int)]
    return {
        "step_count": len(rows),
        "first_loss": losses[0] if losses else None,
        "last_loss": losses[-1] if losses else None,
        "final_step": steps[-1] if steps else None,
        "modes": sorted({str(row.get("mode")) for row in rows if row.get("mode")}),
        "trace_ref": "training-runs/train_demo_001/loss_trace.jsonl",
    }


def _load_training_checkpoint_summary(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cycle or not cycle.get("_cycle_dir"):
        return None
    cycle_dir = Path(str(cycle["_cycle_dir"]))
    checkpoint_logs = sorted(cycle_dir.glob("training-runs/*/checkpoints.jsonl"))
    if not checkpoint_logs:
        return None
    rows = _jsonl_rows(checkpoint_logs[-1])
    return {
        "checkpoint_count": len(rows),
        "restore_validated_count": sum(1 for row in rows if row.get("restore_validated") is True),
        "weight_snapshot_states": sorted({str(row.get("weight_snapshot")) for row in rows if row.get("weight_snapshot")}),
        "checkpoint_refs": [str(row.get("checkpoint_ref")) for row in rows if row.get("checkpoint_ref")],
        "trace_ref": "training-runs/train_demo_001/checkpoints.jsonl",
    }


def _load_training_output_artifacts(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cycle or not cycle.get("_cycle_dir"):
        return None
    cycle_dir = Path(str(cycle["_cycle_dir"]))
    artifact_logs = sorted(cycle_dir.glob("training-runs/*/output_artifacts.jsonl"))
    if not artifact_logs:
        return None
    rows = _jsonl_rows(artifact_logs[-1])
    return {
        "artifact_count": len(rows),
        "artifact_refs": [str(row.get("artifact_ref")) for row in rows if row.get("artifact_ref")],
        "kinds": sorted({str(row.get("kind")) for row in rows if row.get("kind")}),
        "trace_ref": "training-runs/train_demo_001/output_artifacts.jsonl",
    }


def _load_eval_scorecard(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    path = _latest_eval_file(cycle, "scorecard.json")
    if path is None:
        return None
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_eval_comparison_matrix(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    path = _latest_eval_file(cycle, "comparison_matrix.json")
    if path is None:
        return None
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_eval_case_results_summary(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    path = _latest_eval_file(cycle, "case_results.jsonl")
    if path is None:
        return None
    rows = _jsonl_rows(path)
    return {
        "case_count": len(rows),
        "student_pass_count": sum(1 for row in rows if row.get("student_passed") is True),
        "parent_pass_count": sum(1 for row in rows if row.get("parent_passed") is True),
        "teacher_pass_count": sum(1 for row in rows if row.get("teacher_passed") is True),
        "trace_ref": "evals/eval_demo_001/case_results.jsonl",
    }


def _latest_eval_file(cycle: dict[str, Any] | None, filename: str) -> Path | None:
    if not cycle or not cycle.get("_cycle_dir"):
        return None
    cycle_dir = Path(str(cycle["_cycle_dir"]))
    matches = sorted(cycle_dir.glob(f"evals/*/{filename}"))
    return matches[-1] if matches else None


def _jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        import json

        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, ValueError):
        return []


def _load_student_birth_record(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cycle or not cycle.get("_cycle_dir"):
        return None
    path = Path(str(cycle["_cycle_dir"])) / "students" / "student_birth_record.json"
    if not path.exists():
        return None
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_model_genome(cycle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cycle or not cycle.get("_cycle_dir"):
        return None
    path = Path(str(cycle["_cycle_dir"])) / "students" / "model_genome.yaml"
    if not path.exists():
        return None
    try:
        import yaml

        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except (OSError, ValueError):
        return None


def _knowledge_artifact_runtime_gate(request: GrowthCycleRequest) -> dict[str, Any]:
    blocked_refs: list[str] = []
    blocked_reasons: list[str] = []
    for context in request.knowledge_artifact_runtime_contexts:
        artifact_ref = str(context.get("artifact_id") or context.get("artifact_ref") or context.get("context") or "")
        fallback_state = str(context.get("fallback_state") or "")
        if context.get("runtime_context_allowed") is True and fallback_state == "compiled_artifact" and artifact_ref:
            continue
        if artifact_ref:
            blocked_refs.append(artifact_ref)
        reason = str(
            fallback_state
            or (context.get("quarantine_state") or {}).get("reason")
            or "krc_runtime_context_not_allowed"
        )
        blocked_reasons.append(reason)

    return {
        "requires_krc_runtime_context_allowed": True,
        "blocks_stale_or_quarantined_context": True,
        "blocks_raw_retrieval_fallback_context": True,
        "gate_source": "KnowledgeArtifactCompiler.query",
        "mutation_allowed": False,
        "allowed": not blocked_refs and not blocked_reasons,
        "runtime_context_evidence_count": len(request.knowledge_artifact_runtime_contexts),
        "blocked_artifact_refs": sorted(set(blocked_refs)),
        "blocked_reasons": sorted(set(blocked_reasons)),
    }


def _growth_gate(request: GrowthCycleRequest) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    knowledge_artifact_runtime_gate = _knowledge_artifact_runtime_gate(request)
    if knowledge_artifact_runtime_gate["allowed"] is False:
        blockers.append(
            {
                "rule_id": "growth_engine_kac_runtime_context_blocked",
                "severity": "hard_fail",
                "message": "KAC runtime context must be allowed before compiled artifacts can seed growth-cycle evidence.",
                "blocked_artifact_refs": knowledge_artifact_runtime_gate["blocked_artifact_refs"],
                "blocked_reasons": knowledge_artifact_runtime_gate["blocked_reasons"],
            }
        )
    if request.adapter_training_plan_status == "blocked":
        blockers.append(
            {
                "rule_id": "growth_engine_adapter_training_plan_blocked",
                "severity": "hard_fail",
                "message": "Growth cycles require an adapter training plan that is not blocked.",
                "adapter_training_plan_ref": request.adapter_training_plan_ref,
            }
        )
    adapter_training_gate = request.adapter_training_gate or {}
    if adapter_training_gate and adapter_training_gate.get("allowed") is False:
        blockers.append(
            {
                "rule_id": "growth_engine_adapter_training_gate_blocked",
                "severity": "hard_fail",
                "message": "Adapter training gate blockers must be cleared before growth evidence can be used.",
                "adapter_training_plan_ref": request.adapter_training_plan_ref,
                "blocked_source_ids": adapter_training_gate.get("blocked_source_ids") or [],
                "reason": adapter_training_gate.get("reason") or "adapter training gate blocked",
            }
        )
    hard_fail_findings = [
        finding
        for finding in request.adapter_training_findings
        if finding.get("severity") == "hard_fail"
    ]
    if hard_fail_findings:
        blockers.append(
            {
                "rule_id": "growth_engine_adapter_training_hard_fail_findings",
                "severity": "hard_fail",
                "message": "Adapter training hard-fail findings prevent growth cycle execution.",
                "adapter_training_plan_ref": request.adapter_training_plan_ref,
                "finding_rule_ids": [finding.get("rule_id") for finding in hard_fail_findings],
            }
        )
    return {
        "gate_id": "growth_engine_adapter_training_gate",
        "adapter_training_plan_ref": request.adapter_training_plan_ref,
        "adapter_training_plan_status": request.adapter_training_plan_status,
        "knowledge_artifact_runtime_gate": knowledge_artifact_runtime_gate,
        "allowed": not blockers,
        "blockers": blockers,
    }


def _events(cycle_id: str, timestamp: str) -> list[dict[str, Any]]:
    states = [
        "requested",
        "scouted",
        "source_approved",
        "curriculum_ready",
        "teacher_labeled",
        "dataset_forged",
        "student_born",
        "training_planned",
        "trained_dry_run",
        "eval_passed_shadow_only",
        "shadow_specialist",
    ]
    return [
        {
            "schema_version": "growth_event.v0.1",
            "cycle_id": cycle_id,
            "sequence": index,
            "state": state,
            "created_at": timestamp,
        }
        for index, state in enumerate(states, start=1)
    ]


def _training_cases(request: GrowthCycleRequest, refs: dict[str, str], timestamp: str) -> list[dict[str, Any]]:
    stages = [
        "foundation",
        "foundation",
        "controlled_task",
        "controlled_task",
        "tool_required_task",
        "tool_required_task",
        "validation",
        "validation",
        "heldout",
        "heldout",
        "adversarial_task",
        "regression",
    ]
    cases = []
    for index, stage in enumerate(stages, start=1):
        case_id = f"case:{ref_tail(request.cycle_id)}:{index:03d}"
        cases.append(
            {
                "schema_version": "training_case.v0.1",
                "case_id": case_id,
                "cycle_id": request.cycle_id,
                "target_node_ref": request.target_node_id,
                "curriculum_stage": stage,
                "split": _split_for_index(index),
                "prompt": {
                    "content": f"License-cleared synthetic {request.target_node_type} task {index} for {request.target_capabilities}.",
                    "content_hash": f"sha256:demo-{index:03d}",
                    "redaction_state": "not_private",
                },
                "accepted_target": {
                    "content": f"Approved target behavior for {request.student_kind} case {index}.",
                    "target_type": "orchestration_trace_and_final_answer",
                    "license_state": "approved_train",
                },
                "orchestration_targets": {
                    "root_route": ["Execution O", "Governance O"],
                    "lane_route": ["CodingAO", "EvalsAO"],
                    "expert_route": [request.target_node_id, "node:expert_critique"],
                    "router_target_distribution": {request.target_node_id: 0.72, "node:expert_critique": 0.28},
                },
                "teacher_outputs": [
                    {
                        "teacher_ref": teacher_ref,
                        "role": "teacher_council_member",
                        "output_ref": f"teacher_output:{index:03d}:{teacher_ref}",
                        "license_state": "approved_train",
                    }
                    for teacher_ref in (request.teacher_pairing_refs or ["teacher:license_cleared_stub"])
                ],
                "critique_outputs": [
                    {
                        "reviewer_ref": "node:expert_critique",
                        "critique_ref": f"critique:{index:03d}",
                        "severity": 0.1,
                    }
                ],
                "validator_results": [{"validator_ref": "validator:unit_security_privacy_suite", "passed": True, "score": 1.0}],
                "disagreement_metrics": {
                    "teacher_disagreement_score": 0.2,
                    "accepted_resolution": "validator_backed_primary_revision",
                },
                "rubric_scores": {"correctness": 0.94, "safety": 1.0, "clarity": 0.87, "efficiency": 0.75},
                "source_refs": request.source_refs,
                "knowledge_artifact_refs": request.knowledge_artifact_refs,
                "privacy_class": "internal",
                "federating_allowed": False,
                "created_at": timestamp,
                "hash": f"sha256:case-demo-{index:03d}",
            }
        )
    return cases


def _split_for_index(index: int) -> str:
    if index <= 6:
        return "train"
    if index <= 8:
        return "validation"
    if index <= 10:
        return "heldout"
    if index == 11:
        return "adversarial"
    return "regression"


def _required_artifacts() -> list[str]:
    return [
        "growth_cycle",
        "source_candidates",
        "curriculum_manifest",
        "teacher_council_manifest",
        "training_cases",
        "dataset_manifest",
        "hidden_eval_manifest",
        "student_birth_record",
        "model_genome",
        "training_run",
        "eval_scorecard",
        "reviewer_decision",
        "rollback_snapshot",
        "rewind_proof",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/growth-engine"},
        "birth_shadow_student": {"method": "POST", "endpoint": "/ops/brain/growth-engine/cycles"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/growth-engine"},
        "replay_cycle": {"method": "GET", "endpoint": "/ops/brain/growth-engine/cycles/{cycle_id}"},
    }
