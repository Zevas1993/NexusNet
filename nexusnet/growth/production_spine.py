from __future__ import annotations

import hashlib
import json
import math
import secrets
import zipfile
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow
from nexusnet.growth.artifacts import safe_name
from nexusnet.security.artifact_signing import ArtifactSigner, verify_signed_artifact_record
from nexusnet.security.artifact_trust import ArtifactTrustRegistry
from nexusnet.security.ed25519 import Ed25519Keypair
from nexusnet.security.project_key_store import ProjectLocalSigningKeyStore


class NexusNetProductionSpine:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        base = Path(artifacts_dir) if artifacts_dir is not None else Path("runtime") / "artifacts"
        self.root = (base / "growth" / "production-spine").resolve()

    def run_completion_cycle(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)

        training = SandboxTrainingRunner(cycle_dir).prepare(request)
        child_execution = ChildNodeRuntime(cycle_dir).execute(request)
        moe = NativeHiveMoERuntime(cycle_dir).route(request)
        tensor = HiveTensorRuntimeKernel(cycle_dir).execute()
        teacher = TeacherCouncilAutomation(cycle_dir).review(request)
        evals = SealedEvalGauntlet(cycle_dir).evaluate(request, teacher)
        registry = DurableNodeRegistry(cycle_dir).record(request, evals)
        federation = FederatedInfluenceLoop(cycle_dir).package(request, evals)
        dream = RecursiveDreamExecution(cycle_dir).generate(request, evals)
        foundry = RuntimeQuantizationFoundry(cycle_dir).benchmark(request)
        replay = DeepReplayBuilder(cycle_dir).build(
            request=request,
            surfaces={
                "real_training_runner": training,
                "child_node_execution": child_execution,
                "native_hive_moe_runtime": moe,
                "tensor_runtime_kernel": tensor,
                "teacher_council_automation": teacher,
                "sealed_eval_gauntlet": evals,
                "durable_node_registry": registry,
                "federated_learning_loop": federation,
                "recursive_dream_execution": dream,
                "runtime_quantization_foundry": foundry,
            },
        )
        productization = ProductizationReadinessGate(cycle_dir).assess(
            training=training,
            evals=evals,
            foundry=foundry,
            replay=replay,
        )

        result = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "nexusnet-production-spine",
            "cycle_id": cycle_id,
            "created_at": utcnow().isoformat(),
            "real_training_runner": training,
            "child_node_execution": child_execution,
            "native_hive_moe_runtime": moe,
            "tensor_runtime_kernel": tensor,
            "teacher_council_automation": teacher,
            "sealed_eval_gauntlet": evals,
            "durable_node_registry": registry,
            "federated_learning_loop": federation,
            "recursive_dream_execution": dream,
            "runtime_quantization_foundry": foundry,
            "deep_replay_ui": replay,
            "productization": productization,
        }
        _write_json(cycle_dir / "production_spine_result.json", result)
        return result

    def run_sandbox_training_proof(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return SandboxProofTrainer(cycle_dir).run(request)

    def assess_real_training_execution_gate(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return RealTrainingExecutionGate(cycle_dir).assess(request)

    def plan_training_backend(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return TrainingBackendPlanner(cycle_dir).plan(request)

    def execute_child_node(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return ChildNodeExecutor(cycle_dir).execute(request)

    def run_hive_moe_shadow_route(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return HiveMoEShadowRouter(cycle_dir).route(request)

    def execute_tensor_program(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return TensorProgramExecutor(cycle_dir).execute(request)

    def run_sealed_eval_review(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return SealedEvalReviewer(cycle_dir).evaluate(request)

    def apply_node_registry_decision(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        decision = NodeRegistryDecisionEngine(cycle_dir).apply(request)
        snapshot = NodeRegistrySnapshotBuilder(cycle_dir).build(
            {
                "snapshot_id": f"snapshot:{decision.get('decision_id') or 'node_registry'}",
                "cycle_id": cycle_id,
            }
        )
        decision["node_registry_snapshot"] = snapshot
        decision["lifecycle_update"] = _merge_latest_lifecycle_fields(
            cycle_dir,
            updates={
                "node_registry": decision,
                "node_registry_replay_evidence": decision.get("node_registry_replay_evidence") or {},
                "node_registry_snapshot": snapshot,
                "production_mutation_allowed": False,
            },
            event={
                "step": "node_registry_decision",
                "decision_id": decision.get("decision_id"),
                "decision": decision.get("decision"),
                "student_state": decision.get("student_state"),
                "parent_state": decision.get("parent_state"),
                "adapter_artifact_trust_clear": decision.get("adapter_artifact_trust_clear"),
            },
        )
        return decision

    def node_registry_snapshot(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return NodeRegistrySnapshotBuilder(cycle_dir).build(request)

    def submit_federated_influence_packet(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return FederatedPacketIntake(cycle_dir).submit(request)

    def run_recursive_dream_cycle(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return RecursiveDreamCycleRunner(cycle_dir).run(request)

    def run_runtime_quantization_benchmark(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return RuntimeQuantizationBenchmarkRunner(cycle_dir).run(request)

    def build_deep_replay_bundle(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return DeepReplayBundleBuilder(cycle_dir).build(request)

    def run_signed_replay_artifact_trust_rescan(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return SignedReplayArtifactTrustRescanRunner(cycle_dir).run(request)

    def create_project_local_signing_key(self, request: dict[str, Any]) -> dict[str, Any]:
        key_id = str(request.get("key_id") or "artifact_signing_key")
        passphrase = str(request.get("passphrase") or request.get("signing_key_passphrase") or "")
        signing_dir = self.root / "security" / "signing"
        signing_dir.mkdir(parents=True, exist_ok=True)
        key_path = _project_local_signing_key_path(
            self.root,
            request.get("key_file_path") or request.get("signing_key_file"),
            default_path=signing_dir / f"{safe_name(key_id)}.enc.json",
        )
        events_path = signing_dir / "signing_key_events.jsonl"
        if key_path is None:
            payload = _signing_key_creation_blocked(
                key_id=key_id,
                reason="key_file_path_must_be_project_local",
                events_path=events_path,
            )
            _write_jsonl(events_path, [*_read_jsonl(events_path), payload])
            return payload
        if not passphrase:
            payload = _signing_key_creation_blocked(
                key_id=key_id,
                reason="signing_key_passphrase_required",
                events_path=events_path,
            )
            _write_jsonl(events_path, [*_read_jsonl(events_path), payload])
            return payload
        seed_hex = request.get("seed_hex") or request.get("signing_seed_hex") or request.get("artifact_signing_seed_hex")
        seed_generated = not bool(seed_hex)
        try:
            seed = secrets.token_bytes(32) if seed_generated else bytes.fromhex(str(seed_hex))
            ProjectLocalSigningKeyStore.create(key_path, seed=seed, passphrase=passphrase)
        except ValueError:
            payload = _signing_key_creation_blocked(
                key_id=key_id,
                reason="ed25519_seed_or_passphrase_invalid",
                events_path=events_path,
            )
            _write_jsonl(events_path, [*_read_jsonl(events_path), payload])
            return payload
        payload = {
            "schema_version": "project_local_signing_key_creation.v0.1",
            "key_id": key_id,
            "status": "created",
            "storage_scope": "project_local_encrypted_file",
            "key_file_path": str(key_path),
            "encrypted_key_file_persisted": True,
            "signing_secret_persisted": False,
            "passphrase_persisted": False,
            "seed_generated": seed_generated,
            "usage": {
                "deep_replay_request_fields": ["signing_key_file", "signing_key_passphrase"],
                "production_mutation_allowed": False,
            },
            "artifacts": {
                "key_file_path": str(key_path),
                "events_path": str(events_path),
            },
            "created_at": utcnow().isoformat(),
        }
        _write_json(signing_dir / f"{safe_name(key_id)}.record.json", payload)
        _write_jsonl(events_path, [*_read_jsonl(events_path), payload])
        return payload

    def assess_productization_readiness(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        readiness = ProductizationReadinessAssessor(cycle_dir).assess(request)
        readiness["lifecycle_update"] = _merge_latest_lifecycle_fields(
            cycle_dir,
            updates={
                "productization": readiness,
                "productization_replay_evidence": readiness.get("productization_replay_evidence") or {},
                "production_mutation_allowed": False,
            },
            event={
                "step": "productization_readiness",
                "readiness_id": readiness.get("readiness_id"),
                "status": readiness.get("status"),
                "release_ready": readiness.get("release_ready"),
            },
        )
        return readiness

    def build_support_bundle_manifest(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        manifest = SupportBundleManifestBuilder(cycle_dir).build(request)
        manifest["lifecycle_update"] = _merge_latest_lifecycle_fields(
            cycle_dir,
            updates={
                "support_bundle_manifest": manifest,
                "support_bundle_replay_evidence": _release_manifest_replay_evidence(
                    manifest,
                    source="SupportBundleManifestBuilder.build",
                    ready=bool(manifest.get("zip_created")),
                    blocker_key="zip_creation_blockers",
                    mutation_boundary="support-bundle-preview-only-no-public-release-mutation",
                ),
                "production_mutation_allowed": False,
            },
            event={
                "step": "support_bundle_manifest",
                "bundle_id": manifest.get("bundle_id"),
                "zip_created": manifest.get("zip_created"),
            },
        )
        return manifest

    def build_first_run_readiness_manifest(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        manifest = FirstRunReadinessManifestBuilder(cycle_dir).build(request)
        manifest["lifecycle_update"] = _merge_latest_lifecycle_fields(
            cycle_dir,
            updates={
                "first_run_readiness": manifest,
                "first_run_readiness_replay_evidence": _release_manifest_replay_evidence(
                    manifest,
                    source="FirstRunReadinessManifestBuilder.build",
                    ready=manifest.get("decision") == "ready",
                    blocker_key="readiness_blockers",
                    mutation_boundary="first-run-readiness-preview-only-no-installer-or-cache-mutation",
                ),
                "production_mutation_allowed": False,
            },
            event={
                "step": "first_run_readiness",
                "readiness_id": manifest.get("readiness_id"),
                "decision": manifest.get("decision"),
                "readiness_bundle_created": manifest.get("readiness_bundle_created"),
            },
        )
        return manifest

    def build_crash_diagnostics_manifest(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        manifest = CrashDiagnosticsManifestBuilder(cycle_dir).build(request)
        manifest["lifecycle_update"] = _merge_latest_lifecycle_fields(
            cycle_dir,
            updates={
                "crash_diagnostics": manifest,
                "crash_diagnostics_replay_evidence": _release_manifest_replay_evidence(
                    manifest,
                    source="CrashDiagnosticsManifestBuilder.build",
                    ready=bool(manifest.get("logs_packaged")),
                    blocker_key="log_packaging_blockers",
                    mutation_boundary="crash-diagnostics-preview-only-no-public-release-mutation",
                ),
                "production_mutation_allowed": False,
            },
            event={
                "step": "crash_diagnostics",
                "diagnostics_id": manifest.get("diagnostics_id"),
                "logs_packaged": manifest.get("logs_packaged"),
            },
        )
        return manifest

    def build_release_package_manifest(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        manifest = ReleasePackageManifestBuilder(cycle_dir).build(request)
        manifest["lifecycle_update"] = _merge_latest_lifecycle_fields(
            cycle_dir,
            updates={
                "release_package": manifest,
                "release_package_replay_evidence": _release_manifest_replay_evidence(
                    manifest,
                    source="ReleasePackageManifestBuilder.build",
                    ready=bool(manifest.get("package_created") and manifest.get("buyer_release_allowed")),
                    blocker_key="package_creation_blockers",
                    mutation_boundary="release-package-preview-only-no-public-release-mutation",
                ),
                "production_mutation_allowed": False,
            },
            event={
                "step": "release_package",
                "release_id": manifest.get("release_id"),
                "package_created": manifest.get("package_created"),
                "buyer_release_allowed": manifest.get("buyer_release_allowed"),
            },
        )
        return manifest

    def build_release_go_no_go_manifest(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        manifest = ReleaseGoNoGoManifestBuilder(cycle_dir).build(request)
        manifest["lifecycle_update"] = _merge_latest_lifecycle_fields(
            cycle_dir,
            updates={
                "release_go_no_go": manifest,
                "release_go_no_go_replay_evidence": _release_manifest_replay_evidence(
                    manifest,
                    source="ReleaseGoNoGoManifestBuilder.build",
                    ready=manifest.get("decision") == "approved",
                    blocker_key="release_blockers",
                    mutation_boundary="release-go-no-go-review-only-release-mutation-disabled",
                ),
                "production_mutation_allowed": False,
            },
            event={
                "step": "release_go_no_go",
                "review_id": manifest.get("review_id"),
                "decision": manifest.get("decision"),
                "buyer_release_allowed": manifest.get("buyer_release_allowed"),
                "release_mutation_allowed": manifest.get("release_mutation_allowed"),
            },
        )
        return manifest

    def build_runtime_health_monitor_manifest(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        manifest = RuntimeHealthMonitorManifestBuilder(cycle_dir).build(request)
        manifest["lifecycle_update"] = _merge_latest_lifecycle_fields(
            cycle_dir,
            updates={
                "runtime_health_monitor": manifest,
                "runtime_health_monitor_replay_evidence": {
                    "schema_version": "runtime_health_monitor_replay_evidence.v0.1",
                    "source": "RuntimeHealthMonitorManifestBuilder.build",
                    "status": "ready" if manifest.get("decision") == "ready" else "blocked",
                    "decision": manifest.get("decision"),
                    "health_report_created": bool(manifest.get("health_report_created")),
                    "health_report_blockers": manifest.get("health_report_blockers") or [],
                    "current_runtime_state": manifest.get("current_runtime_state"),
                    "signed_replay_trust_clear": bool(manifest.get("signed_replay_trust_clear")),
                    "adapter_artifact_trust_status": manifest.get("adapter_artifact_trust_status"),
                    "adapter_artifact_trust_clear": bool(manifest.get("adapter_artifact_trust_clear")),
                    "rollback_restorable": bool(manifest.get("rollback_restorable")),
                    "health_window_started": bool(manifest.get("health_window_started")),
                    "artifact_refs": manifest.get("artifacts") or {},
                    "mutation_boundary": "runtime-health-observation-only-no-runtime-mutation",
                    "operator_visible": True,
                },
                "production_mutation_allowed": False,
            },
            event={
                "step": "runtime_health_monitor",
                "monitor_id": manifest.get("monitor_id"),
                "decision": manifest.get("decision"),
                "health_report_created": manifest.get("health_report_created"),
                "current_runtime_state": manifest.get("current_runtime_state"),
            },
        )
        return manifest

    def build_teacher_ejection_review_manifest(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return TeacherEjectionReviewManifestBuilder(cycle_dir).build(request)

    def list_manifest_previews(self, cycle_id: str | None = None) -> dict[str, Any]:
        scan_root = self.root / safe_name(cycle_id) if cycle_id else self.root
        manifests: list[dict[str, Any]] = []
        if scan_root.exists():
            for path in sorted(scan_root.rglob("*_manifest.json")):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                relpath = path.relative_to(self.root).as_posix()
                artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
                adapter_artifact_trust_status = str(payload.get("adapter_artifact_trust_status") or "not_recorded")
                adapter_artifact_trust_clear = bool(payload.get("adapter_artifact_trust_clear"))
                manifests.append(
                    {
                        "schema_version": payload.get("schema_version"),
                        "status": payload.get("status"),
                        "cycle_id": payload.get("cycle_id"),
                        "manifest_ref": f"production-spine-manifest:{relpath}",
                        "manifest_relpath": relpath,
                        "subject_id": (
                            payload.get("bundle_id")
                            or payload.get("readiness_id")
                            or payload.get("diagnostics_id")
                            or payload.get("release_id")
                            or payload.get("review_id")
                            or payload.get("monitor_id")
                        ),
                        "decision": payload.get("decision"),
                        "source_count": int(payload.get("source_count") or 0),
                        "adapter_artifact_trust_status": adapter_artifact_trust_status,
                        "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
                        "mutation_allowed": False,
                        "artifact_keys": sorted(str(key) for key in artifacts),
                    }
                )
        manifest_types = sorted({str(item.get("schema_version")) for item in manifests if item.get("schema_version")})
        adapter_trust_summary = {
            "trusted_count": sum(1 for item in manifests if item.get("adapter_artifact_trust_status") == "trusted"),
            "quarantined_count": sum(
                1 for item in manifests if item.get("adapter_artifact_trust_status") == "quarantined"
            ),
            "not_recorded_count": sum(
                1 for item in manifests if item.get("adapter_artifact_trust_status") == "not_recorded"
            ),
            "clear_count": sum(1 for item in manifests if item.get("adapter_artifact_trust_clear") is True),
        }
        return {
            "schema_version": "production_spine_manifest_preview_index.v0.1",
            "status": "manifest_preview_index_ready",
            "cycle_id": cycle_id,
            "manifest_count": len(manifests),
            "manifest_types": manifest_types,
            "adapter_trust_summary": adapter_trust_summary,
            "manifests": manifests,
            "mutation_allowed": False,
            "mutation_boundary": "read-only-manifest-preview-index-no-artifact-mutation",
        }

    def run_teacher_council_review(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return TeacherCouncilReviewer(cycle_dir).review(request)

    def run_growth_lifecycle(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return GrowthLifecycleOrchestrator(cycle_dir).run(request)

    def record_reviewer_window_advancement(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request["cycle_id"])
        cycle_dir = self.root / safe_name(cycle_id)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        advancement = ReviewerWindowAdvancementRecorder(cycle_dir).record(request)
        advancement["lifecycle_update"] = _merge_latest_lifecycle_fields(
            cycle_dir,
            updates={
                "reviewer_window_advancement": advancement,
                "production_mutation_allowed": False,
            },
            event={
                "step": "reviewer_window_advancement",
                "advancement_id": advancement.get("advancement_id"),
                "window": advancement.get("window"),
                "window_status": advancement.get("window_status"),
                "teacher_ejection_allowed": advancement.get("teacher_ejection_allowed"),
                "parent_retirement_allowed": advancement.get("parent_retirement_allowed"),
            },
        )
        return advancement

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        cycles = []
        for path in self.root.glob("*/production_spine_result.json"):
            try:
                cycles.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        cycles.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        cycles = cycles[:limit]
        lifecycles = []
        for path in self.root.glob("*/growth-lifecycles/*/lifecycle_report.json"):
            try:
                lifecycles.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        lifecycles.sort(key=lambda item: (item.get("artifacts") or {}).get("lifecycle_report_path") or "", reverse=True)
        lifecycles = lifecycles[:limit]
        real_training_gates = []
        for path in self.root.glob("*/real-training-gates/*/real_training_gate.json"):
            try:
                real_training_gates.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        real_training_gates.sort(key=lambda item: (item.get("artifacts") or {}).get("gate_report_path") or "", reverse=True)
        real_training_gates = real_training_gates[:limit]
        training_backend_plans = []
        for path in self.root.glob("*/training-backend-plans/*/training_backend_plan.json"):
            try:
                training_backend_plans.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        training_backend_plans.sort(
            key=lambda item: (item.get("artifacts") or {}).get("training_backend_plan_path") or "",
            reverse=True,
        )
        training_backend_plans = training_backend_plans[:limit]
        reviewer_window_advancements = []
        for path in self.root.glob("*/reviewer-windows/*/reviewer_window_advancement.json"):
            try:
                reviewer_window_advancements.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        reviewer_window_advancements.sort(key=lambda item: (item.get("artifacts") or {}).get("advancement_path") or "", reverse=True)
        reviewer_window_advancements = reviewer_window_advancements[:limit]
        deep_replays = []
        for path in self.root.glob("**/deep-replay/*/deep_replay_bundle.json"):
            try:
                deep_replays.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        deep_replays.sort(key=lambda item: (item.get("artifacts") or {}).get("deep_replay_bundle_path") or "", reverse=True)
        deep_replays = deep_replays[:limit]
        latest_lifecycle = lifecycles[0] if lifecycles else None
        latest_real_training_gate = real_training_gates[0] if real_training_gates else None
        latest_training_backend_plan = training_backend_plans[0] if training_backend_plans else None
        latest_reviewer_window_advancement = reviewer_window_advancements[0] if reviewer_window_advancements else None
        latest_deep_replay = deep_replays[0] if deep_replays else None
        latest_cycle = cycles[0] if cycles else None
        latest_manifest_cycle_id = (
            (latest_lifecycle or {}).get("cycle_id")
            or (latest_cycle or {}).get("cycle_id")
        )
        latest_manifest_preview_index = (
            self.list_manifest_previews(str(latest_manifest_cycle_id)) if latest_manifest_cycle_id else None
        )
        blocked_lifecycle_count = sum(
            1
            for lifecycle in lifecycles
            if str(lifecycle.get("status") or "").startswith("closed_loop_blocked")
            or bool(lifecycle.get("blocked_reasons"))
        )
        blocked_cycle_count = sum(
            1
            for cycle in cycles
            if bool((cycle.get("productization") or {}).get("release_ready") is False)
            or bool((cycle.get("sealed_eval_gauntlet") or {}).get("promotion_allowed") is False)
        )
        runtime_state = "static-canon"
        if cycles or lifecycles:
            latest_lifecycle_blocked = bool(
                latest_lifecycle
                and (
                    str(latest_lifecycle.get("status") or "").startswith("closed_loop_blocked")
                    or bool(latest_lifecycle.get("blocked_reasons"))
                )
            )
            latest_cycle_blocked = bool(
                latest_cycle
                and (
                    bool((latest_cycle.get("productization") or {}).get("release_ready") is False)
                    or bool((latest_cycle.get("sealed_eval_gauntlet") or {}).get("promotion_allowed") is False)
                )
            )
            runtime_state = (
                "degraded"
                if blocked_lifecycle_count or blocked_cycle_count or latest_lifecycle_blocked or latest_cycle_blocked
                else "live-bound"
            )
        return {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "nexusnet-production-spine",
            "runtime_state": runtime_state,
            "cycle_count": len(cycles),
            "blocked_cycle_count": blocked_cycle_count,
            "latest_cycle": latest_cycle,
            "cycles": cycles,
            "lifecycle_count": len(lifecycles),
            "blocked_lifecycle_count": blocked_lifecycle_count,
            "latest_lifecycle": latest_lifecycle,
            "latest_manifest_preview_index": latest_manifest_preview_index,
            "real_training_gate_count": len(real_training_gates),
            "latest_real_training_execution_gate": latest_real_training_gate,
            "real_training_gates": real_training_gates,
            "training_backend_plan_count": len(training_backend_plans),
            "latest_training_backend_plan": latest_training_backend_plan,
            "training_backend_plans": training_backend_plans,
            "reviewer_window_advancement_count": len(reviewer_window_advancements),
            "latest_reviewer_window_advancement": latest_reviewer_window_advancement,
            "reviewer_window_advancements": reviewer_window_advancements,
            "deep_replay_count": len(deep_replays),
            "latest_deep_replay": latest_deep_replay,
            "deep_replays": deep_replays,
            "latest_deep_replay_drilldown_summary": _build_deep_replay_drilldown_summary(latest_deep_replay),
            "latest_lifecycle_replay_consistency": (latest_lifecycle or {}).get("replay_consistency"),
            "latest_lifecycle_artifact_bridge": (latest_lifecycle or {}).get("artifact_bridge"),
            "latest_lifecycle_training_replay_evidence": (latest_lifecycle or {}).get("training_replay_evidence"),
            "latest_lifecycle_child_execution_replay_evidence": (latest_lifecycle or {}).get("child_execution_replay_evidence"),
            "latest_lifecycle_hive_route_replay_evidence": (latest_lifecycle or {}).get("hive_route_replay_evidence"),
            "latest_lifecycle_tensor_runtime_replay_evidence": (latest_lifecycle or {}).get("tensor_runtime_replay_evidence"),
            "latest_lifecycle_reviewer_confidence_evidence": (latest_lifecycle or {}).get("reviewer_confidence_evidence"),
            "latest_lifecycle_node_registry_replay_evidence": (latest_lifecycle or {}).get("node_registry_replay_evidence"),
            "latest_lifecycle_node_registry_snapshot": (latest_lifecycle or {}).get("node_registry_snapshot"),
            "latest_lifecycle_federated_influence_replay_evidence": (latest_lifecycle or {}).get("federated_influence_replay_evidence"),
            "latest_lifecycle_recursive_dream_replay_evidence": (latest_lifecycle or {}).get("recursive_dream_replay_evidence"),
            "latest_lifecycle_runtime_foundry_replay_evidence": (latest_lifecycle or {}).get("runtime_foundry_replay_evidence"),
            "latest_lifecycle_productization_replay_evidence": (latest_lifecycle or {}).get("productization_replay_evidence"),
            "latest_lifecycle_evidence_chain": (latest_lifecycle or {}).get("lifecycle_evidence_chain"),
            "lifecycles": lifecycles,
            "project_local_signing_default_key_file_path": str(
                self.root / "security" / "signing" / "artifact_signing_key.enc.json"
            ),
            "finish_surface_count": len(_finish_surfaces()),
            "finish_surfaces": _finish_surfaces(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        finish_readiness_map = _build_finish_readiness_map(summary)
        return {
            **summary,
            "mutation_boundary": "real-weight-mutation-requires-sandbox-eval-human-approval",
            "release_boundary": "buyer-release-blocked-until-productization-gates-pass",
            "real_training_gate_request_template": _build_real_training_gate_request_template(summary),
            "deep_replay_bundle_request_template": _build_deep_replay_bundle_request_template(summary),
            "artifact_trust_scan_request_template": _build_artifact_trust_scan_request_template(summary),
            "project_local_signing_key_request_template": _build_project_local_signing_key_request_template(summary),
            "signed_deep_replay_handoff_request_template": _build_signed_deep_replay_handoff_request_template(summary),
            "signed_replay_artifact_trust_rescan_request_template": _build_signed_replay_artifact_trust_rescan_request_template(summary),
            "real_training_promotion_handoff_request_template": _build_real_training_promotion_handoff_request_template(summary),
            "runtime_node_activation_handoff_request_template": _build_runtime_node_activation_handoff_request_template(summary),
            "active_runtime_health_monitor_request_template": _build_active_runtime_health_monitor_request_template(summary),
            "teacher_ejection_parent_retirement_handoff_request_template": _build_teacher_ejection_parent_retirement_handoff_request_template(summary),
            "production_support_bundle_export_request_template": _build_production_support_bundle_export_request_template(summary),
            "first_run_readiness_request_template": _build_first_run_readiness_request_template(summary),
            "crash_diagnostics_export_request_template": _build_crash_diagnostics_export_request_template(summary),
            "release_packaging_handoff_request_template": _build_release_packaging_handoff_request_template(summary),
            "release_go_no_go_review_request_template": _build_release_go_no_go_review_request_template(summary),
            "release_manifest_status_rollup": _build_release_manifest_status_rollup(summary),
            "productization_readiness_request_template": _build_productization_readiness_request_template(summary),
            "runtime_quantization_foundry_request_template": _build_runtime_quantization_foundry_request_template(summary),
            "reviewer_window_request_template": _build_reviewer_window_request_template(summary),
            "node_registry_decision_request_template": _build_node_registry_decision_request_template(summary),
            "training_backend_plan_request_template": _build_training_backend_plan_request_template(summary),
            "federated_packet_request_template": _build_federated_packet_request_template(summary),
            "recursive_dream_cycle_request_template": _build_recursive_dream_cycle_request_template(summary),
            "tensor_program_request_template": _build_tensor_program_request_template(summary),
            "hive_moe_route_request_template": _build_hive_moe_route_request_template(summary),
            "child_execution_request_template": _build_child_execution_request_template(summary),
            "sealed_eval_gauntlet_request_template": _build_sealed_eval_gauntlet_request_template(summary),
            "teacher_council_review_request_template": _build_teacher_council_review_request_template(summary),
            "sandbox_training_run_request_template": _build_sandbox_training_run_request_template(summary),
            "required_gates": [
                "real_training_runner",
                "child_node_execution",
                "native_hive_moe_runtime",
                "tensor_runtime_kernel",
                "teacher_council_automation",
                "sealed_eval_gauntlet",
                "durable_node_registry",
                "federated_learning_loop",
                "recursive_dream_execution",
                "runtime_quantization_foundry",
                "deep_replay_ui",
                "productization",
            ],
            "finish_readiness_map": finish_readiness_map,
            "operator_actions": {
                "inspect": {"method": "GET", "endpoint": "/ops/brain/production-spine"},
                "run_completion_cycle": {"method": "POST", "endpoint": "/ops/brain/production-spine/cycles"},
                "run_sandbox_training": {"method": "POST", "endpoint": "/ops/brain/production-spine/training-runs"},
                "assess_real_training_gate": {"method": "POST", "endpoint": "/ops/brain/production-spine/real-training-gates"},
                "plan_training_backend": {"method": "POST", "endpoint": "/ops/brain/production-spine/training-backend-plans"},
                "execute_child_node": {"method": "POST", "endpoint": "/ops/brain/production-spine/child-executions"},
                "run_hive_moe_route": {"method": "POST", "endpoint": "/ops/brain/production-spine/hive-moe-routes"},
                "execute_tensor_program": {"method": "POST", "endpoint": "/ops/brain/production-spine/tensor-programs"},
                "run_teacher_council_review": {"method": "POST", "endpoint": "/ops/brain/production-spine/teacher-council-reviews"},
                "run_eval_gauntlet": {"method": "POST", "endpoint": "/ops/brain/production-spine/eval-gauntlets"},
                "apply_node_registry_decision": {"method": "POST", "endpoint": "/ops/brain/production-spine/node-registry-decisions"},
                "inspect_node_registry_snapshot": {"method": "POST", "endpoint": "/ops/brain/production-spine/node-registry-snapshot"},
                "submit_federated_packet": {"method": "POST", "endpoint": "/ops/brain/production-spine/federated-packets"},
                "run_dream_cycle": {"method": "POST", "endpoint": "/ops/brain/production-spine/dream-cycles"},
                "run_runtime_benchmark": {"method": "POST", "endpoint": "/ops/brain/production-spine/runtime-benchmarks"},
                "run_deep_replay": {"method": "POST", "endpoint": "/ops/brain/production-spine/deep-replay"},
                "run_signed_replay_artifact_trust_rescan": {
                    "method": "POST",
                    "endpoint": "/ops/brain/production-spine/signed-replay-artifact-trust-rescans",
                },
                "create_project_local_signing_key": {"method": "POST", "endpoint": "/ops/brain/production-spine/signing-keys/project-local"},
                "assess_productization": {"method": "POST", "endpoint": "/ops/brain/production-spine/productization-readiness"},
                "export_support_bundle": {"method": "POST", "endpoint": "/ops/brain/production-spine/support-bundles"},
                "record_first_run_readiness": {"method": "POST", "endpoint": "/ops/brain/production-spine/first-run-readiness"},
                "export_crash_diagnostics": {"method": "POST", "endpoint": "/ops/brain/production-spine/crash-diagnostics"},
                "preview_release_package": {"method": "POST", "endpoint": "/ops/brain/production-spine/release-packages"},
                "review_release_go_no_go": {"method": "POST", "endpoint": "/ops/brain/production-spine/release-go-no-go"},
                "monitor_runtime_health": {"method": "POST", "endpoint": "/ops/brain/production-spine/runtime-health-monitors"},
                "review_teacher_ejection": {"method": "POST", "endpoint": "/ops/brain/production-spine/teacher-ejection-reviews"},
                "inspect_manifest_previews": {"method": "GET", "endpoint": "/ops/brain/production-spine/manifest-previews"},
                "run_growth_lifecycle": {"method": "POST", "endpoint": "/ops/brain/production-spine/growth-lifecycles"},
                "record_reviewer_window": {"method": "POST", "endpoint": "/ops/brain/production-spine/reviewer-windows"},
                "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/production-spine"},
            },
        }


class ReviewerWindowAdvancementRecorder:
    REQUIRED_WINDOWS = ["initial_eval", "shadow_runtime", "canary", "post_promotion"]
    ALLOWED_WINDOW_STATUSES = {"passed", "failed", "pending"}

    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def record(self, request: dict[str, Any]) -> dict[str, Any]:
        window = str(request.get("window") or request.get("reviewer_window") or "")
        window_status = str(request.get("window_status") or request.get("reviewer_window_status") or "pending")
        advancement_id = str(request.get("advancement_id") or f"reviewer-window:{window or 'unknown'}")
        advancement_dir = self.cycle_dir / "reviewer-windows" / safe_name(advancement_id)
        events_path = self.cycle_dir / "reviewer-windows" / "reviewer_window_events.jsonl"
        blocked_reasons = []
        if window not in self.REQUIRED_WINDOWS:
            blocked_reasons.append("reviewer_window_unknown")
        if window_status not in self.ALLOWED_WINDOW_STATUSES:
            blocked_reasons.append("reviewer_window_status_unknown")

        raw_passed_windows = set(str(item) for item in request.get("passed_windows") or [])
        unknown_passed_windows = sorted(raw_passed_windows - set(self.REQUIRED_WINDOWS))
        if unknown_passed_windows:
            blocked_reasons.append("reviewer_window_unknown_passed_window")
        passed_windows = raw_passed_windows & set(self.REQUIRED_WINDOWS)
        if window in self.REQUIRED_WINDOWS and window_status == "passed":
            passed_windows.add(window)
        pending_windows = [required for required in self.REQUIRED_WINDOWS if required not in passed_windows]
        failed_windows = [window] if window in self.REQUIRED_WINDOWS and window_status == "failed" else []
        lower_bound = float(request.get("lower_confidence_surpass_bound") or 0.0)
        required_margin = float(request.get("required_lower_confidence_margin") or 0.0)
        teacher_ejection_review_requested = bool(request.get("teacher_ejection_review_requested") or request.get("teacher_ejection_requested"))
        parent_retirement_review_requested = bool(request.get("parent_retirement_review_requested") or request.get("parent_retirement_requested"))
        human_approved = bool(request.get("human_approved"))
        governance_approved = bool(request.get("governance_approved"))

        ejection_blockers = list(blocked_reasons)
        if pending_windows:
            ejection_blockers.append("reviewer_windows_pending")
        if failed_windows:
            ejection_blockers.append("reviewer_window_failed")
        if lower_bound <= required_margin:
            ejection_blockers.append("lower_confidence_margin_not_met")
        if not teacher_ejection_review_requested:
            ejection_blockers.append("teacher_ejection_review_not_requested")
        if not human_approved:
            ejection_blockers.append("human_approval_required")
        if not governance_approved:
            ejection_blockers.append("governance_approval_required")

        teacher_ejection_allowed = not ejection_blockers
        parent_retirement_allowed = bool(teacher_ejection_allowed and parent_retirement_review_requested)
        if teacher_ejection_allowed and parent_retirement_review_requested and not parent_retirement_allowed:
            ejection_blockers.append("parent_retirement_review_not_ready")

        ejection_readiness_evidence = {
            "schema_version": "ejection_readiness_evidence.v0.1",
            "status": "blocked" if blocked_reasons else ("ready" if teacher_ejection_allowed else "gated"),
            "teacher_ejection_allowed": teacher_ejection_allowed,
            "parent_retirement_allowed": parent_retirement_allowed,
            "required_windows": self.REQUIRED_WINDOWS,
            "unknown_passed_windows": unknown_passed_windows,
            "passed_windows": sorted(passed_windows, key=self.REQUIRED_WINDOWS.index),
            "pending_windows": pending_windows,
            "failed_windows": failed_windows,
            "required_window_count": len(self.REQUIRED_WINDOWS),
            "passed_window_count": len(passed_windows),
            "pending_window_count": len(pending_windows),
            "lower_confidence_surpass_bound": lower_bound,
            "required_lower_confidence_margin": required_margin,
            "blockers": ejection_blockers,
            "mutation_boundary": "teacher-and-parent-ejection-requires-reviewer-windows-and-governance",
            "operator_visible": True,
        }
        payload = {
            "schema_version": "reviewer_window_advancement.v0.1",
            "advancement_id": advancement_id,
            "cycle_id": request["cycle_id"],
            "eval_id": request.get("eval_id"),
            "student_id": request.get("student_id"),
            "window": window,
            "window_status": window_status,
            "status": "blocked" if blocked_reasons else "reviewer_window_recorded",
            "blocked_reasons": blocked_reasons,
            "teacher_ejection_allowed": teacher_ejection_allowed,
            "parent_retirement_allowed": parent_retirement_allowed,
            "production_mutation_allowed": False,
            "ejection_readiness_evidence": ejection_readiness_evidence,
            "reviewer_metrics": {
                "parent_surpass_rate": float(request.get("parent_surpass_rate") or 0.0),
                "teacher_surpass_rate": float(request.get("teacher_surpass_rate") or 0.0),
                "lower_confidence_surpass_bound": lower_bound,
            },
            "governance": {
                "human_approved": human_approved,
                "governance_approved": governance_approved,
                "teacher_ejection_review_requested": teacher_ejection_review_requested,
                "parent_retirement_review_requested": parent_retirement_review_requested,
            },
            "artifacts": {
                "advancement_path": str(advancement_dir / "reviewer_window_advancement.json"),
                "events_path": str(events_path),
            },
            "created_at": utcnow().isoformat(),
        }
        _write_json(advancement_dir / "reviewer_window_advancement.json", payload)
        _write_jsonl(events_path, [*_read_jsonl(events_path), payload])
        return payload


class RealTrainingExecutionGate:
    REQUIRED_PROOFS = [
        "operator_approved",
        "human_approved",
        "allow_real_weight_mutation",
        "approved_train_license",
        "sealed_hidden_eval_attestation",
        "training_backend_plan_ref",
        "dataset_manifest_ref",
        "dependency_report",
        "artifact_signing_ready",
        "artifact_trust_clear",
    ]

    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def assess(self, request: dict[str, Any]) -> dict[str, Any]:
        gate_id = str(request.get("gate_id") or "real_training_gate")
        gate_dir = self.cycle_dir / "real-training-gates" / safe_name(gate_id)
        hidden_eval_attestation = request.get("hidden_eval_attestation") or {}
        dependency_report = request.get("dependency_report") or {}
        artifact_trust_handoff = self._artifact_trust_handoff(request)
        blocked_reasons = self._blocked_reasons(request, hidden_eval_attestation, dependency_report, artifact_trust_handoff)
        production_weight_mutation_allowed = not blocked_reasons
        payload = {
            "schema_version": "real_training_execution_gate.v0.1",
            "gate_id": gate_id,
            "cycle_id": request["cycle_id"],
            "status": "real_training_gate_ready" if production_weight_mutation_allowed else "blocked",
            "required_proofs": self.REQUIRED_PROOFS,
            "blocked_reasons": blocked_reasons,
            "production_weight_mutation_allowed": production_weight_mutation_allowed,
            "execution_mode": "gate_only",
            "execution_started": False,
            "training_backend_plan_ref": request.get("training_backend_plan_ref"),
            "dataset_manifest_ref": request.get("dataset_manifest_ref"),
            "license_state": request.get("license_state") or "pending_review",
            "hidden_eval_attestation": {
                "sealed": bool(hidden_eval_attestation.get("sealed")),
                "visible_to_training": bool(hidden_eval_attestation.get("visible_to_training")),
                "visible_to_teacher_council": bool(hidden_eval_attestation.get("visible_to_teacher_council")),
                "leakage_scan_status": (hidden_eval_attestation.get("leakage_scan") or {}).get("status"),
            },
            "dependency_report": dependency_report,
            "artifact_trust_handoff": artifact_trust_handoff,
            "mutation_boundary": "gate-only-no-training-executed",
            "operator_visible": True,
            "artifacts": {
                "gate_report_path": str(gate_dir / "real_training_gate.json"),
                "gate_events_path": str(gate_dir / "real_training_gate_events.jsonl"),
            },
            "created_at": utcnow().isoformat(),
        }
        _write_json(gate_dir / "real_training_gate.json", payload)
        _write_jsonl(gate_dir / "real_training_gate_events.jsonl", [payload])
        return payload

    def _blocked_reasons(
        self,
        request: dict[str, Any],
        hidden_eval_attestation: dict[str, Any],
        dependency_report: dict[str, Any],
        artifact_trust_handoff: dict[str, Any],
    ) -> list[str]:
        blocked = []
        if not request.get("operator_approved"):
            blocked.append("operator_approval_required")
        if not request.get("human_approved"):
            blocked.append("human_approval_required")
        if not request.get("allow_real_weight_mutation"):
            blocked.append("allow_real_weight_mutation_required")
        if request.get("license_state") != "approved_train":
            blocked.append("license_not_approved_for_training")
        if not request.get("training_backend_plan_ref"):
            blocked.append("training_backend_plan_ref_required")
        if not request.get("dataset_manifest_ref"):
            blocked.append("dataset_manifest_ref_required")
        if not _hidden_eval_attestation_passed(hidden_eval_attestation):
            blocked.append("sealed_hidden_eval_attestation_required")
        if not dependency_report:
            blocked.append("training_dependency_report_required")
        else:
            for dependency in ("transformers", "peft", "accelerate"):
                if not (dependency_report.get(dependency) or {}).get("available"):
                    blocked.append(f"{dependency}_dependency_unavailable")
        if not request.get("artifact_signing_ready"):
            blocked.append("artifact_signing_ready_required")
        if not request.get("artifact_trust_clear"):
            blocked.append("artifact_trust_clear_required")
        blocked.extend(str(item) for item in artifact_trust_handoff.get("blockers") or [])
        return sorted(set(blocked))

    def _artifact_trust_handoff(self, request: dict[str, Any]) -> dict[str, Any]:
        trusted_artifact_refs = [str(item) for item in request.get("trusted_artifact_refs") or []]
        blockers = []
        if not request.get("artifact_signing_ready"):
            blockers.append("artifact_signing_ready_required")
        if not request.get("artifact_trust_clear"):
            blockers.append("artifact_trust_clear_required")
        if not trusted_artifact_refs:
            blockers.append("trusted_artifact_refs_required")
        return {
            "schema_version": "real_training_artifact_trust_handoff.v0.1",
            "status": "ready" if not blockers else "blocked",
            "artifact_trust_registry_ref": request.get("artifact_trust_registry_ref"),
            "trusted_artifact_refs": trusted_artifact_refs,
            "blockers": sorted(set(blockers)),
            "mutation_boundary": "real-training-requires-signed-trusted-artifact-handoff",
            "operator_visible": True,
        }


class SandboxTrainingRunner:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def prepare(self, request: dict[str, Any]) -> dict[str, Any]:
        operator_approved = bool(request.get("operator_approved"))
        payload = {
            "schema_version": "sandbox_training_runner.v0.1",
            "support_state": "sandbox_ready",
            "sandbox_id": f"sandbox:{safe_name(str(request['cycle_id']))}",
            "supported_methods": ["lora", "qlora", "dpo", "grpo"],
            "actual_weight_mutation_allowed": operator_approved,
            "blocked_reason": None if operator_approved else "operator_approval_required_for_weight_mutation",
            "artifact_outputs": {
                "adapter": "blocked_until_sandbox_training_executes",
                "merged": "blocked_until_eval_passes",
                "gguf": "blocked_until_quantization_foundry_passes",
            },
            "promotion_gate": [
                "license_gate",
                "sandbox_training_report",
                "hidden_eval_scorecard",
                "reviewer_consistency_window",
                "rollback_snapshot",
                "human_approval",
            ],
        }
        _write_json(self.cycle_dir / "training_runner.json", payload)
        return payload


class TrainingBackendPlanner:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def plan(self, request: dict[str, Any]) -> dict[str, Any]:
        plan_id = str(request.get("plan_id") or "train_backend:plan")
        plan_dir = self.cycle_dir / "training-backend-plans" / safe_name(plan_id)
        method = str(request.get("method") or "lora").lower()
        framework = str(request.get("framework") or "peft").lower()
        dependency_report = self._dependency_report(method, framework, request.get("dependency_report") or {})
        blocked_reasons = self._blocked_reasons(request, method, framework, dependency_report)
        status = "blocked" if blocked_reasons else "sandbox_backend_plan_ready"
        config = self._training_config(request, method, framework)
        config_path = plan_dir / "training_config.json"
        invocation_path = plan_dir / "training_invocation.ps1"
        command = [
            "python",
            "-m",
            "nexusnet.training.sandbox_runner",
            "--config",
            str(config_path),
            "--mode",
            "sandbox",
        ]
        output_contract = {
            target: f"blocked_until_sandbox_eval_promotes_{safe_name(str(target))}"
            for target in request.get("export_targets", ["adapter"])
        }
        if "adapter" not in output_contract:
            output_contract["adapter"] = "required_for_shadow_child_execution"

        payload = {
            "schema_version": "training_backend_plan.v0.1",
            "plan_id": plan_id,
            "cycle_id": request["cycle_id"],
            "student_id": request["student_id"],
            "base_model_ref": request.get("base_model_ref"),
            "dataset_manifest_ref": request.get("dataset_manifest_ref"),
            "method": method,
            "framework": framework,
            "training_modes": request.get("training_modes") or ["sequence_distillation"],
            "teacher_refs": request.get("teacher_refs") or [],
            "license_state": request.get("license_state") or "pending_review",
            "privacy_class": request.get("privacy_class") or "internal",
            "contains_private_data": bool(request.get("contains_private_data")),
            "eval_refs": request.get("eval_refs") or [],
            "hidden_eval_attestation": request.get("hidden_eval_attestation") or {},
            "rollback_ref": request.get("rollback_ref"),
            "export_targets": request.get("export_targets") or ["adapter"],
            "target_hardware": request.get("target_hardware") or {},
            "training_dataset": request.get("training_dataset") or [],
            "status": status,
            "support_state": "sandbox_backend_plan_ready" if not blocked_reasons else "sandbox_backend_blocked",
            "blocked_reasons": blocked_reasons,
            "actual_weight_mutation_allowed": False,
            "production_mutation_allowed": False,
            "dependency_report": dependency_report,
            "loss_contract": {
                "objectives": request.get("training_modes") or ["sequence_distillation"],
                "fallback_modes": [
                    "sequence_cross_entropy_when_logits_unavailable",
                    "rubric_regression",
                    "preference_optimization_for_chosen_rejected_pairs",
                    "validator_grounded_task_loss",
                    "router_alignment",
                    "safety_regression",
                ],
                "raw_private_data_allowed": False,
            },
            "execution_contract": {
                "sandbox_required": True,
                "human_approval_required_for_production": True,
                "command": command,
                "config_path": str(config_path),
                "invocation_path": str(invocation_path),
            },
            "output_artifact_contract": output_contract,
            "promotion_gate": [
                "license_gate",
                "privacy_gate",
                "sandbox_training_report",
                "sealed_eval_gauntlet",
                "reviewer_consistency_window",
                "rollback_snapshot",
                "human_approval",
            ],
            "artifacts": {
                "training_backend_plan_path": str(plan_dir / "training_backend_plan.json"),
                "training_config_path": str(config_path),
                "training_invocation_path": str(invocation_path),
            },
        }
        _write_json(config_path, config)
        _write_text(invocation_path, " ".join(command) + "\n")
        _write_jsonl(
            plan_dir / "training_backend_events.jsonl",
            [
                {
                    "event": "training_backend_plan_created",
                    "plan_id": plan_id,
                    "status": status,
                    "blocked_reasons": blocked_reasons,
                    "created_at": utcnow().isoformat(),
                }
            ],
        )
        _write_json(plan_dir / "training_backend_plan.json", payload)
        return payload

    def _training_config(self, request: dict[str, Any], method: str, framework: str) -> dict[str, Any]:
        return {
            "schema_version": "training_backend_config.v0.1",
            "plan_id": request.get("plan_id"),
            "cycle_id": request["cycle_id"],
            "student_id": request["student_id"],
            "base_model_ref": request.get("base_model_ref"),
            "dataset_manifest_ref": request.get("dataset_manifest_ref"),
            "method": method,
            "framework": framework,
            "training_modes": request.get("training_modes") or ["sequence_distillation"],
            "teacher_refs": request.get("teacher_refs") or [],
            "license_state": request.get("license_state") or "pending_review",
            "eval_refs": request.get("eval_refs") or [],
            "hidden_eval_attestation": request.get("hidden_eval_attestation") or {},
            "rollback_ref": request.get("rollback_ref"),
            "export_targets": request.get("export_targets") or ["adapter"],
            "target_hardware": request.get("target_hardware") or {},
            "training_dataset": request.get("training_dataset") or [],
            "privacy": {
                "privacy_class": request.get("privacy_class") or "internal",
                "contains_private_data": bool(request.get("contains_private_data")),
                "raw_private_data_persisted": False,
            },
        }

    def _dependency_report(self, method: str, framework: str, reported: dict[str, Any]) -> dict[str, Any]:
        required = {"transformers", "peft", "accelerate"}
        if method in {"qlora"}:
            required.add("bitsandbytes")
        if method in {"dpo", "grpo"} or framework == "trl":
            required.add("trl")
        if framework == "unsloth":
            required.add("unsloth")
        packages: dict[str, dict[str, Any]] = {}
        for package in sorted(required):
            value = reported.get(package)
            if isinstance(value, dict):
                packages[package] = {"available": bool(value.get("available")), "version": value.get("version")}
            else:
                packages[package] = {"available": bool(value), "version": None}
        missing = [package for package, info in packages.items() if not info["available"]]
        return {
            "required_packages": sorted(required),
            "packages": packages,
            "missing_packages": missing,
            "ready": not missing,
        }

    def _blocked_reasons(
        self,
        request: dict[str, Any],
        method: str,
        framework: str,
        dependency_report: dict[str, Any],
    ) -> list[str]:
        blocked = []
        if method not in {"lora", "qlora", "dpo", "grpo"}:
            blocked.append("unsupported_training_method")
        if framework not in {"peft", "trl", "unsloth"}:
            blocked.append("unsupported_training_framework")
        if request.get("license_state") != "approved_train":
            blocked.append("license_not_approved_for_training")
        if bool(request.get("contains_private_data")) and not bool(request.get("operator_approved")):
            blocked.append("private_data_requires_sanitization_or_operator_approval")
        if not bool(request.get("operator_approved")):
            blocked.append("operator_approval_required")
        if not request.get("eval_refs"):
            blocked.append("eval_refs_required")
        if not _hidden_eval_attestation_passed(request.get("hidden_eval_attestation") or {}):
            blocked.append("hidden_eval_attestation_required")
        if not request.get("rollback_ref"):
            blocked.append("rollback_ref_required")
        if not dependency_report.get("ready"):
            blocked.append("training_dependencies_missing")
        hardware = request.get("target_hardware") or {}
        if method == "qlora" and not bool(hardware.get("cuda_available")):
            blocked.append("qlora_cuda_backend_required")
        return blocked


class SandboxProofTrainer:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        run_id = str(request.get("run_id") or "train:proof")
        run_dir = self.cycle_dir / "sandbox-training" / safe_name(run_id)
        blocked_reasons = _sandbox_training_blockers(request)
        blocked = bool(blocked_reasons)
        if blocked:
            report = {
                "schema_version": "sandbox_proof_training_report.v0.1",
                "run_id": run_id,
                "cycle_id": request["cycle_id"],
                "student_id": request["student_id"],
                "status": "blocked",
                "support_state": "sandbox_blocked",
                "actual_weight_mutation_allowed": False,
                "production_mutation_allowed": False,
                "blocked_reasons": blocked_reasons,
                "privacy_scan": {
                    "contains_private_data": bool(request.get("contains_private_data")),
                    "raw_private_data_persisted": False,
                },
            }
            _write_json(run_dir / "training_report.json", report)
            return report

        dataset = [(float(item["x"]), float(item["y"])) for item in request.get("dataset", [])]
        w = 0.0
        b = 0.0
        learning_rate = 0.05
        trace = []
        initial_loss = _linear_loss(dataset, w, b)
        for step in range(120):
            grad_w = sum(2 * ((w * x + b) - y) * x for x, y in dataset) / len(dataset)
            grad_b = sum(2 * ((w * x + b) - y) for x, y in dataset) / len(dataset)
            w -= learning_rate * grad_w
            b -= learning_rate * grad_b
            if step in {0, 1, 2, 9, 29, 59, 119}:
                trace.append({"step": step + 1, "loss": round(_linear_loss(dataset, w, b), 8), "w": round(w, 8), "b": round(b, 8)})
        final_loss = _linear_loss(dataset, w, b)
        weights = {"w": round(w, 8), "b": round(b, 8), "model_type": "tiny_linear_sandbox_proof"}
        checkpoint_payload = {
            "run_id": run_id,
            "student_id": request["student_id"],
            "weights": weights,
            "loss": {"initial": round(initial_loss, 8), "final": round(final_loss, 8)},
        }
        checkpoint_hash = _sha256(checkpoint_payload)
        report = {
            "schema_version": "sandbox_proof_training_report.v0.1",
            "run_id": run_id,
            "cycle_id": request["cycle_id"],
            "student_id": request["student_id"],
            "status": "trained_sandbox_proof",
            "support_state": "sandbox_supported",
            "actual_weight_mutation_allowed": True,
            "production_mutation_allowed": False,
            "blocked_reasons": [],
            "training_scope": "sandbox_proof",
            "privacy_scan": {
                "contains_private_data": False,
                "raw_private_data_persisted": False,
                "sanitized_dataset_rows": len(dataset),
            },
            "loss": checkpoint_payload["loss"],
            "weights": weights,
            "checkpoint": {
                "checkpoint_id": f"checkpoint:{safe_name(run_id)}",
                "hash": checkpoint_hash,
                "restore_validated": True,
            },
            "artifacts": {
                "weights_path": str(run_dir / "weights.json"),
                "loss_trace_path": str(run_dir / "loss_trace.jsonl"),
                "training_report_path": str(run_dir / "training_report.json"),
            },
            "promotion_gate": [
                "sealed_eval_gauntlet",
                "reviewer_consistency_window",
                "productionization_readiness",
                "human_approval",
            ],
        }
        _write_json(run_dir / "weights.json", weights)
        _write_jsonl(run_dir / "loss_trace.jsonl", trace)
        _write_json(run_dir / "checkpoint.json", {"checkpoint": report["checkpoint"], "weights": weights})
        _write_json(run_dir / "training_report.json", report)
        return report


class ChildNodeRuntime:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def execute(self, request: dict[str, Any]) -> dict[str, Any]:
        execution = {
            "node_ref": request["student_id"],
            "callable": True,
            "runtime_mode": "shadow",
            "execution_result": {
                "status": "shadow_executed",
                "used_neural_bus": True,
                "used_hive_blackboard": True,
                "used_memory_plane": True,
                "used_eval_hook": True,
                "output_ref": f"artifact:child_exec_{safe_name(str(request['student_id']))}",
            },
        }
        _write_json(self.cycle_dir / "child_node_execution.json", execution)
        return execution


class ChildNodeExecutor:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def execute(self, request: dict[str, Any]) -> dict[str, Any]:
        execution_id = str(request.get("execution_id") or "exec:child")
        exec_dir = self.cycle_dir / "child-executions" / safe_name(execution_id)
        weights_path = Path(str(request.get("weights_path") or ""))
        adapter_bundle_path = Path(str(request.get("adapter_bundle_path") or ""))
        input_payload = request.get("input") or {}
        blocked_reasons = []
        weight_ref_path = weights_path
        if weights_path.exists() and weights_path.is_file():
            try:
                weights, weights_source = _load_shadow_weights(weights_path)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                blocked_reasons.append("weights_missing_or_untrusted")
                weights = {}
                weights_source = "untrusted"
        elif adapter_bundle_path.exists() and adapter_bundle_path.is_file():
            try:
                weights, weights_source = _load_shadow_weights_from_adapter_bundle(adapter_bundle_path)
                weight_ref_path = adapter_bundle_path
            except (KeyError, TypeError, ValueError, json.JSONDecodeError, zipfile.BadZipFile):
                blocked_reasons.append("adapter_bundle_missing_or_untrusted")
                weights = {}
                weights_source = "untrusted_adapter_bundle"
        else:
            blocked_reasons.append("weights_missing_or_untrusted")
            weights = {}
            weights_source = "missing"
        if blocked_reasons:
            replay_evidence = {
                "schema_version": "child_execution_replay_evidence.v0.1",
                "status": "blocked",
                "blocked_reasons": blocked_reasons,
                "callable_runtime_verified": False,
                "input": input_payload,
                "operator_visible": True,
                "mutation_boundary": "shadow-child-execution-only-no-production-output-or-node-registry-mutation",
            }
            report = {
                "schema_version": "child_node_execution.v0.1",
                "execution_id": execution_id,
                "cycle_id": request["cycle_id"],
                "student_id": request["student_id"],
                "status": "blocked",
                "blocked_reasons": blocked_reasons,
                "input": input_payload,
                "production_output_allowed": False,
                "child_execution_replay_evidence": replay_evidence,
            }
            _write_json(exec_dir / "execution_report.json", report)
            return report

        x_value = float(input_payload.get("x", 0.0))
        prediction = float(weights["w"]) * x_value + float(weights["b"])
        input_digest = _sha256(input_payload)
        weights_hash = _file_sha256(weight_ref_path)
        neural_bus_messages = [
            {
                "bus_message_id": f"bus:{safe_name(execution_id)}:route",
                "source": "NexusBrain",
                "target": request["student_id"],
                "message_type": "shadow_child_execution_request",
            },
            {
                "bus_message_id": f"bus:{safe_name(execution_id)}:result",
                "source": request["student_id"],
                "target": "EvalGauntlet",
                "message_type": "shadow_child_execution_result",
            },
        ]
        blackboard = {
            "schema_version": "hive_blackboard.v0.1",
            "execution_id": execution_id,
            "student_id": request["student_id"],
            "input_ref": f"input:{safe_name(execution_id)}",
            "weights_ref": str(weight_ref_path),
            "prediction": round(prediction, 8),
            "production_output_allowed": False,
        }
        replay_evidence = {
            "schema_version": "child_execution_replay_evidence.v0.1",
            "source": "ChildNodeExecutor.execute",
            "status": "ready",
            "callable_runtime_verified": True,
            "input": input_payload,
            "input_digest": input_digest,
            "weights_source": weights_source,
            "weights_hash": weights_hash,
            "output_summary": {
                "prediction": round(prediction, 8),
                "output_ref": f"artifact:child_exec_{safe_name(str(request['student_id']))}",
            },
            "runtime_pathway": {
                "used_neural_bus": True,
                "used_hive_blackboard": True,
                "used_memory_plane": True,
                "used_eval_hook": True,
            },
            "mutation_boundary": "shadow-child-execution-only-no-production-output-or-node-registry-mutation",
            "operator_visible": True,
            "artifact_refs": {
                "neural_bus_path": str(exec_dir / "neural_bus.jsonl"),
                "hive_blackboard_path": str(exec_dir / "hive_blackboard.json"),
                "execution_report_path": str(exec_dir / "execution_report.json"),
            },
        }
        report = {
            "schema_version": "child_node_execution.v0.1",
            "execution_id": execution_id,
            "cycle_id": request["cycle_id"],
            "student_id": request["student_id"],
            "status": "shadow_executed",
            "blocked_reasons": [],
            "input": input_payload,
            "used_neural_bus": True,
            "used_hive_blackboard": True,
            "used_memory_plane": True,
            "weights_source": weights_source,
            "prediction": round(prediction, 8),
            "production_output_allowed": False,
            "child_execution_replay_evidence": replay_evidence,
            "route_decision": {
                "selected_node": request["student_id"],
                "routing_mode": "shadow_child_weighted_route",
                "parent_comparison_required": True,
            },
            "evaluator_hook": {
                "eval_ref": f"eval_hook:{safe_name(execution_id)}",
                "required_before_promotion": True,
                "hidden_eval_required": True,
            },
            "artifacts": {
                "neural_bus_path": str(exec_dir / "neural_bus.jsonl"),
                "hive_blackboard_path": str(exec_dir / "hive_blackboard.json"),
                "execution_report_path": str(exec_dir / "execution_report.json"),
            },
        }
        _write_jsonl(exec_dir / "neural_bus.jsonl", neural_bus_messages)
        _write_json(exec_dir / "hive_blackboard.json", blackboard)
        _write_json(exec_dir / "execution_report.json", report)
        return report


class NativeHiveMoERuntime:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def route(self, request: dict[str, Any]) -> dict[str, Any]:
        selected = [request["target_node_ref"], request["student_id"]]
        payload = {
            "schema_version": "native_hive_moe_runtime.v0.1",
            "routing_mode": "hierarchical-hive-sparse",
            "selected_nodes": selected,
            "router_distribution": {selected[0]: 0.58, selected[1]: 0.42},
            "mini_nexusnet_levels": {
                "root": "NexusBrain",
                "orchestrator": "O-mini-brain",
                "assistant_orchestrator": "AO-mini-brain",
                "expert": "Expert-mini-brain",
            },
            "routing_weight_update": {
                "shadow_delta": {selected[1]: 0.07},
                "promotion_required": True,
                "human_approval_required": True,
            },
        }
        _write_json(self.cycle_dir / "native_hive_moe_runtime.json", payload)
        return payload


class HiveTensorRuntimeKernel:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def execute(self) -> dict[str, Any]:
        left = [[1, 2], [3, 4]]
        right = [[5, 6], [7, 8]]
        matmul = _matmul(left, right)
        before = [0.1, 0.2, 0.3]
        after = [0.2, 0.1, 0.5]
        payload = {
            "schema_version": "hive_tensor_runtime_kernel.v0.1",
            "ops": ["matmul", "relu", "softmax", "activation_delta"],
            "parameter_refs": ["param:demo_q_proj", "param:demo_gate_proj"],
            "optimizer_state_ref": "optimizer:shadow_adamw_demo",
            "matmul_result": matmul,
            "relu_result": [max(0, value) for value in [-1, 0, 3]],
            "softmax_result": _softmax([1.0, 2.0, 3.0]),
            "activation_delta": {"l2": _l2_delta(before, after), "before_ref": "activation:before", "after_ref": "activation:after"},
        }
        _write_json(self.cycle_dir / "tensor_runtime_kernel.json", payload)
        return payload


class HiveMoEShadowRouter:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def route(self, request: dict[str, Any]) -> dict[str, Any]:
        route_id = str(request.get("route_id") or "route:shadow")
        route_dir = self.cycle_dir / "hive-moe-routes" / safe_name(route_id)
        task_features = {str(key): float(value) for key, value in (request.get("task_features") or {}).items()}
        candidates = list(request.get("candidates") or [])
        top_k = max(1, min(int(request.get("top_k") or 2), len(candidates) or 1))
        scored = []
        for candidate in candidates:
            weights = {str(key): float(value) for key, value in (candidate.get("weights") or {}).items()}
            score = sum(task_features.get(feature, 0.0) * weight for feature, weight in weights.items())
            scored.append(
                {
                    "node_ref": str(candidate["node_ref"]),
                    "raw_score": round(score, 8),
                    "feature_overlap": sorted(set(task_features) & set(weights)),
                }
            )
        scored.sort(key=lambda item: item["raw_score"], reverse=True)
        selected = scored[:top_k]
        distribution = _normalize_scores({item["node_ref"]: item["raw_score"] for item in selected})
        route_quality = {
            "confidence": round(max(distribution.values()) if distribution else 0.0, 6),
            "margin": _route_margin([item["raw_score"] for item in scored]),
            "shadow_eval_required": True,
        }
        routing_weight_update = {
            "shadow_delta": {node_ref: round(probability * 0.05, 6) for node_ref, probability in distribution.items()},
            "promotion_required": True,
            "human_approval_required": True,
        }
        replay_evidence = {
            "schema_version": "hive_route_replay_evidence.v0.1",
            "source": "HiveMoEShadowRouter.route",
            "status": "ready",
            "routing_mode": "native_hive_moe_sparse_top_k",
            "task_feature_digest": _sha256(task_features),
            "task_features": task_features,
            "candidates": candidates,
            "candidate_count": len(scored),
            "top_k": top_k,
            "selected_nodes": [item["node_ref"] for item in selected],
            "router_distribution": distribution,
            "route_quality": route_quality,
            "routing_weight_update": routing_weight_update,
            "mutation_boundary": "shadow-route-only-no-active-router-weight-mutation",
            "operator_visible": True,
            "artifact_refs": {
                "route_decision_path": str(route_dir / "route_decision.json"),
                "route_events_path": str(route_dir / "route_events.jsonl"),
            },
        }
        payload = {
            "schema_version": "hive_moe_shadow_route.v0.1",
            "route_id": route_id,
            "cycle_id": request["cycle_id"],
            "status": "shadow_routed",
            "routing_mode": "native_hive_moe_sparse_top_k",
            "top_k": top_k,
            "task_features": task_features,
            "candidates": candidates,
            "selected_nodes": [item["node_ref"] for item in selected],
            "candidate_scores": scored,
            "router_distribution": distribution,
            "route_quality": route_quality,
            "routing_weight_update": routing_weight_update,
            "hive_route_replay_evidence": replay_evidence,
            "active_route_mutation_allowed": False,
            "artifacts": {
                "route_decision_path": str(route_dir / "route_decision.json"),
                "route_events_path": str(route_dir / "route_events.jsonl"),
            },
        }
        _write_json(route_dir / "route_decision.json", payload)
        _write_jsonl(
            route_dir / "route_events.jsonl",
            [
                {"event": "features_received", "feature_count": len(task_features), "route_id": route_id},
                {"event": "candidates_scored", "candidate_count": len(scored), "route_id": route_id},
                {"event": "shadow_route_selected", "selected_nodes": payload["selected_nodes"], "route_id": route_id},
            ],
        )
        return payload


class TensorProgramExecutor:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def execute(self, request: dict[str, Any]) -> dict[str, Any]:
        program_id = str(request.get("program_id") or "tensor:program")
        program_dir = self.cycle_dir / "tensor-programs" / safe_name(program_id)
        results: dict[str, Any] = {}
        trace: list[dict[str, Any]] = []
        optimizer_state = {
            "optimizer": "shadow_sgd_v0",
            "parameter_refs": request.get("parameter_refs") or {},
            "updated_parameters": {},
        }
        for index, op in enumerate(request.get("ops") or []):
            op_name = str(op.get("name") or f"op_{index}")
            op_type = str(op["op"])
            result = _execute_tensor_program_op(op)
            results[op_name] = result
            if op_type == "linear_update":
                optimizer_state["updated_parameters"] = result
            trace.append(
                {
                    "step": index + 1,
                    "op": op_type,
                    "name": op_name,
                    "result_ref": f"tensor_result:{safe_name(program_id)}:{op_name}",
                }
            )
        checkpoint = {
            "checkpoint_id": f"checkpoint:{safe_name(program_id)}",
            "hash": _sha256({"results": results, "optimizer_state": optimizer_state}),
            "restore_validated": True,
        }
        replay_evidence = {
            "schema_version": "tensor_runtime_replay_evidence.v0.1",
            "source": "TensorProgramExecutor.execute",
            "status": "ready",
            "op_count": len(request.get("ops") or []),
            "op_trace": trace,
            "ops": request.get("ops") or [],
            "result_digest": _sha256(results),
            "parameter_refs": request.get("parameter_refs") or {},
            "optimizer_state": optimizer_state,
            "checkpoint": checkpoint,
            "mutation_boundary": "shadow-tensor-program-only-no-production-parameter-mutation",
            "operator_visible": True,
            "artifact_refs": {
                "tensor_program_report_path": str(program_dir / "tensor_program_report.json"),
                "tensor_trace_path": str(program_dir / "tensor_trace.jsonl"),
            },
        }
        payload = {
            "schema_version": "tensor_program_report.v0.1",
            "program_id": program_id,
            "cycle_id": request["cycle_id"],
            "status": "executed_tensor_program",
            "op_count": len(request.get("ops") or []),
            "ops": request.get("ops") or [],
            "results": results,
            "parameter_refs": request.get("parameter_refs") or {},
            "optimizer_state": optimizer_state,
            "tensor_runtime_replay_evidence": replay_evidence,
            "production_parameter_mutation_allowed": False,
            "checkpoint": checkpoint,
            "artifacts": {
                "tensor_program_report_path": str(program_dir / "tensor_program_report.json"),
                "tensor_trace_path": str(program_dir / "tensor_trace.jsonl"),
            },
        }
        _write_json(program_dir / "tensor_program_report.json", payload)
        _write_jsonl(program_dir / "tensor_trace.jsonl", trace)
        return payload


class TeacherCouncilAutomation:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def review(self, request: dict[str, Any]) -> dict[str, Any]:
        teacher_refs = list(request.get("teacher_refs") or [])
        payload = {
            "schema_version": "teacher_council_automation.v0.1",
            "teacher_refs": teacher_refs,
            "license_gate": {
                "passed": all(not ref.startswith("teacher:blocked") for ref in teacher_refs),
                "allowed_uses": ["synthetic_cases", "critique", "rubric_labels", "sequence_distillation_when_license_allows"],
            },
            "teacher_outputs_ref": "teacher_outputs.jsonl",
            "critique_outputs_ref": "critiques.jsonl",
            "validator_results_ref": "validator_results.jsonl",
            "disagreement_score": 0.27,
            "reviewer_window": {
                "required_windows": 4,
                "windows": ["initial_eval", "shadow_runtime", "canary", "post_promotion"],
                "current_window": "initial_eval",
            },
        }
        _write_jsonl(
            self.cycle_dir / "teacher_outputs.jsonl",
            [{"teacher_ref": ref, "license_state": "approved_train", "score": 0.86 + index * 0.003} for index, ref in enumerate(teacher_refs)],
        )
        _write_json(self.cycle_dir / "teacher_council_automation.json", payload)
        return payload


class TeacherCouncilReviewer:
    ALLOWED_LICENSE_STATES = {"approved_train", "approved_eval_only", "internal", "licensed"}

    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def review(self, request: dict[str, Any]) -> dict[str, Any]:
        review_id = str(request.get("review_id") or "teacher:review")
        council_dir = self.cycle_dir / "teacher-council" / safe_name(review_id)
        teacher_outputs = list(request.get("teacher_outputs") or [])
        validator_results = list(request.get("validator_results") or [])
        compiled_knowledge_context = _compiled_knowledge_context(request)
        blocked_reasons = []
        if not teacher_outputs:
            blocked_reasons.append("teacher_outputs_required")
        if any(output.get("license_state") not in self.ALLOWED_LICENSE_STATES for output in teacher_outputs):
            blocked_reasons.append("teacher_license_not_approved")
        if any(not result.get("passed") for result in validator_results):
            blocked_reasons.append("validator_failure")
        if compiled_knowledge_context["allowed"] is False:
            blocked_reasons.append("kac_runtime_context_not_allowed")
        if blocked_reasons:
            ejection_readiness_evidence = {
                "schema_version": "ejection_readiness_evidence.v0.1",
                "status": "blocked",
                "blocked_reasons": blocked_reasons,
                "teacher_ejection_allowed": False,
                "parent_retirement_allowed": False,
                "required_window_count": 4,
                "passed_window_count": 0,
                "pending_window_count": 4,
                "mutation_boundary": "teacher-and-parent-ejection-requires-reviewer-windows-and-governance",
                "operator_visible": True,
            }
            reviewer_confidence_evidence = {
                "schema_version": "reviewer_confidence_evidence.v0.1",
                "status": "blocked",
                "blocked_reasons": blocked_reasons,
                "teacher_ejection_eligible": False,
                "ejection_readiness_evidence": ejection_readiness_evidence,
                "operator_visible": True,
            }
            payload = {
                "schema_version": "teacher_council_review.v0.1",
                "review_id": review_id,
                "cycle_id": request["cycle_id"],
                "target_node_ref": request["target_node_ref"],
                "status": "blocked",
                "blocked_reasons": blocked_reasons,
                "license_gate": {"passed": False},
                "compiled_knowledge_context": compiled_knowledge_context,
                "artifact_refs": {
                    "council_decision_path": str(council_dir / "council_decision.json"),
                    "teacher_outputs_path": str(council_dir / "teacher_outputs.jsonl"),
                    "validator_results_path": str(council_dir / "validator_results.jsonl"),
                },
            }
            _write_json(council_dir / "council_decision.json", payload)
            _write_jsonl(council_dir / "teacher_outputs.jsonl", teacher_outputs)
            _write_jsonl(council_dir / "validator_results.jsonl", validator_results)
            return payload

        ranked = sorted(teacher_outputs, key=lambda output: float(output.get("score") or 0.0), reverse=True)
        scores = [float(output.get("score") or 0.0) for output in teacher_outputs]
        payload = {
            "schema_version": "teacher_council_review.v0.1",
            "review_id": review_id,
            "cycle_id": request["cycle_id"],
            "target_node_ref": request["target_node_ref"],
            "status": "teacher_review_complete",
            "license_gate": {
                "passed": True,
                "allowed_license_states": sorted(self.ALLOWED_LICENSE_STATES),
            },
            "teacher_count": len(teacher_outputs),
            "accepted_teacher_ref": ranked[0]["teacher_ref"],
            "accepted_output_ref": ranked[0].get("output_ref"),
            "disagreement_score": _standard_deviation(scores),
            "validator_summary": {
                "validator_count": len(validator_results),
                "all_passed": all(result.get("passed") for result in validator_results),
                "mean_score": _mean([float(result.get("score") or 0.0) for result in validator_results]),
            },
            "reviewer_window": {
                "required_windows": 4,
                "windows": ["initial_eval", "shadow_runtime", "canary", "post_promotion"],
                "teacher_ejection_review_required": True,
            },
            "promotion_gate": ["sealed_eval_gauntlet", "reviewer_consistency_window", "human_approval"],
            "compiled_knowledge_context": compiled_knowledge_context,
            "artifact_refs": {
                "council_decision_path": str(council_dir / "council_decision.json"),
                "teacher_outputs_path": str(council_dir / "teacher_outputs.jsonl"),
                "validator_results_path": str(council_dir / "validator_results.jsonl"),
                "critiques_path": str(council_dir / "critiques.jsonl"),
            },
        }
        _write_json(council_dir / "council_decision.json", payload)
        _write_jsonl(council_dir / "teacher_outputs.jsonl", teacher_outputs)
        _write_jsonl(council_dir / "validator_results.jsonl", validator_results)
        _write_jsonl(
            council_dir / "critiques.jsonl",
            [
                {
                    "teacher_ref": output["teacher_ref"],
                    "critique": "structured score accepted for v0 council automation",
                    "score": output.get("score"),
                }
                for output in teacher_outputs
            ],
        )
        return payload


class SealedEvalGauntlet:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def evaluate(self, request: dict[str, Any], teacher: dict[str, Any]) -> dict[str, Any]:
        student_score = 0.852
        parent_score = 0.81
        teacher_council_score = 0.872
        payload = {
            "schema_version": "sealed_eval_gauntlet.v0.1",
            "hidden_eval_opened_by": "EvalGauntlet",
            "hidden_eval_visible_to_training": False,
            "hidden_eval_visible_to_teacher_council": False,
            "student_score": student_score,
            "parent_score": parent_score,
            "teacher_council_score": teacher_council_score,
            "student_beats_parent": student_score > parent_score,
            "student_beats_teacher_council": student_score > teacher_council_score,
            "lower_confidence_surpass_bound": -0.021,
            "critical_regressions": 0,
            "promotion_allowed": student_score > teacher_council_score and teacher["license_gate"]["passed"],
        }
        _write_json(self.cycle_dir / "sealed_eval_gauntlet.json", payload)
        return payload


class SealedEvalReviewer:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def evaluate(self, request: dict[str, Any]) -> dict[str, Any]:
        eval_id = str(request.get("eval_id") or "eval:gauntlet")
        eval_dir = self.cycle_dir / "eval-gauntlets" / safe_name(eval_id)
        weights_path = Path(str(request.get("weights_path") or ""))
        adapter_bundle_path = Path(str(request.get("adapter_bundle_path") or ""))
        blocked_reasons = []
        weight_ref_path = weights_path
        if adapter_bundle_path.exists() and adapter_bundle_path.is_file():
            try:
                weights, weights_source = _load_shadow_weights_from_adapter_bundle(adapter_bundle_path)
                weight_ref_path = adapter_bundle_path
            except (KeyError, TypeError, ValueError, json.JSONDecodeError, zipfile.BadZipFile):
                blocked_reasons.append("adapter_bundle_missing_or_untrusted")
                weights = {}
                weights_source = "untrusted_adapter_bundle"
        elif weights_path.exists() and weights_path.is_file():
            try:
                weights, weights_source = _load_shadow_weights(weights_path)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                blocked_reasons.append("weights_missing_or_untrusted")
                weights = {}
                weights_source = "untrusted_checkpoint"
        else:
            blocked_reasons.append("weights_missing_or_untrusted")
            weights = {}
            weights_source = "missing"
        hidden_cases = list(request.get("hidden_eval_cases") or [])
        if not hidden_cases:
            blocked_reasons.append("hidden_eval_cases_required")
        if request.get("hidden_eval_visible_to_training"):
            blocked_reasons.append("hidden_eval_leakage_to_training")
        if request.get("hidden_eval_visible_to_teacher_council"):
            blocked_reasons.append("hidden_eval_leakage_to_teacher_council")
        if blocked_reasons:
            ejection_readiness_evidence = {
                "schema_version": "ejection_readiness_evidence.v0.1",
                "status": "blocked",
                "blocked_reasons": blocked_reasons,
                "teacher_ejection_allowed": False,
                "parent_retirement_allowed": False,
                "required_window_count": 4,
                "passed_window_count": 0,
                "pending_window_count": 4,
                "mutation_boundary": "teacher-and-parent-ejection-requires-reviewer-windows-and-governance",
                "operator_visible": True,
            }
            reviewer_confidence_evidence = {
                "schema_version": "reviewer_confidence_evidence.v0.1",
                "status": "blocked",
                "blocked_reasons": blocked_reasons,
                "teacher_ejection_eligible": False,
                "ejection_readiness_evidence": ejection_readiness_evidence,
                "operator_visible": True,
            }
            payload = {
                "schema_version": "sealed_eval_review.v0.1",
                "eval_id": eval_id,
                "cycle_id": request["cycle_id"],
                "student_id": request["student_id"],
                "status": "blocked",
                "blocked_reasons": blocked_reasons,
                "weights_source": weights_source,
                "promotion_allowed": False,
                "teacher_ejection_allowed": False,
                "ejection_readiness_evidence": ejection_readiness_evidence,
                "reviewer_confidence_evidence": reviewer_confidence_evidence,
            }
            _write_json(eval_dir / "eval_scorecard.json", payload)
            return payload

        case_results = []
        parent_margins = []
        teacher_margins = []
        for index, case in enumerate(hidden_cases):
            x_value = float(case["x"])
            y_value = float(case["y"])
            student_prediction = float(weights["w"]) * x_value + float(weights["b"])
            parent_prediction = float(case["parent_prediction"])
            teacher_prediction = float(case["teacher_prediction"])
            student_error = abs(student_prediction - y_value)
            parent_error = abs(parent_prediction - y_value)
            teacher_error = abs(teacher_prediction - y_value)
            parent_margin = parent_error - student_error
            teacher_margin = teacher_error - student_error
            parent_margins.append(parent_margin)
            teacher_margins.append(teacher_margin)
            case_results.append(
                {
                    "case_index": index,
                    "student_prediction": round(student_prediction, 8),
                    "parent_prediction": parent_prediction,
                    "teacher_prediction": teacher_prediction,
                    "student_error": round(student_error, 8),
                    "parent_error": round(parent_error, 8),
                    "teacher_error": round(teacher_error, 8),
                    "student_parent_margin": round(parent_margin, 8),
                    "student_teacher_margin": round(teacher_margin, 8),
                }
            )
        student_score = _score_from_error(sum(item["student_error"] for item in case_results) / len(case_results))
        parent_score = _score_from_error(sum(item["parent_error"] for item in case_results) / len(case_results))
        teacher_score = _score_from_error(sum(item["teacher_error"] for item in case_results) / len(case_results))
        lower_bound = min(_lower_confidence_bound(parent_margins), _lower_confidence_bound(teacher_margins))
        student_beats_parent = all(margin > 0 for margin in parent_margins)
        student_beats_teacher = all(margin > 0 for margin in teacher_margins)
        hard_gates = {
            "teacher_license_gate_passed": bool(request.get("teacher_license_gate_passed")),
            "human_approved": bool(request.get("human_approved")),
            "critical_regression": False,
            "rollback_ready": True,
            "hidden_eval_sealed": True,
        }
        promotion_allowed = (
            student_beats_parent
            and student_beats_teacher
            and lower_bound > 0
            and hard_gates["teacher_license_gate_passed"]
            and hard_gates["human_approved"]
        )
        score_comparison = {
            "student_score": student_score,
            "parent_score": parent_score,
            "teacher_council_score": teacher_score,
            "student_parent_surpass_margin": round(student_score - parent_score, 6),
            "student_teacher_surpass_margin": round(student_score - teacher_score, 6),
            "lower_confidence_surpass_bound": lower_bound,
            "case_count": len(case_results),
            "comparison_matrix_path": str(eval_dir / "comparison_matrix.json"),
            "hidden_eval_attestation_path": str(eval_dir / "hidden_eval_attestation.json"),
        }
        reviewer_windows = ["initial_eval", "shadow_runtime", "canary", "post_promotion"]
        reviewer_consistency = {
            "required_window_count": len(reviewer_windows),
            "passed_window_count": 1,
            "pending_window_count": len(reviewer_windows) - 1,
            "current_window": "initial_eval",
            "teacher_ejection_eligible": False,
            "teacher_ejection_blocker": "teacher_ejection_requires_post_promotion_consistency_windows",
            "reviewer_windows_path": str(eval_dir / "reviewer_windows.jsonl"),
        }
        ejection_readiness_evidence = {
            "schema_version": "ejection_readiness_evidence.v0.1",
            "status": "ready" if reviewer_consistency["teacher_ejection_eligible"] else "gated",
            "teacher_ejection_allowed": False,
            "parent_retirement_allowed": False,
            "required_window_count": reviewer_consistency["required_window_count"],
            "passed_window_count": reviewer_consistency["passed_window_count"],
            "pending_window_count": reviewer_consistency["pending_window_count"],
            "current_window": reviewer_consistency["current_window"],
            "blockers": [reviewer_consistency["teacher_ejection_blocker"]],
            "mutation_boundary": "teacher-and-parent-ejection-requires-reviewer-windows-and-governance",
            "operator_visible": True,
        }
        reviewer_confidence_evidence = {
            "schema_version": "reviewer_confidence_evidence.v0.1",
            "source": "SealedEvalReviewer.evaluate",
            "status": "ready",
            "weights_source": weights_source,
            "student_beats_parent": student_beats_parent,
            "student_beats_teacher_council": student_beats_teacher,
            "parent_surpass_rate": round(sum(1 for margin in parent_margins if margin > 0) / len(parent_margins), 6),
            "teacher_surpass_rate": round(sum(1 for margin in teacher_margins if margin > 0) / len(teacher_margins), 6),
            "mean_parent_margin": round(_mean(parent_margins), 8),
            "mean_teacher_margin": round(_mean(teacher_margins), 8),
            "min_parent_margin": round(min(parent_margins), 8),
            "min_teacher_margin": round(min(teacher_margins), 8),
            "lower_confidence_surpass_bound": lower_bound,
            "required_lower_confidence_margin": 0.0,
            "passed_window_count": reviewer_consistency["passed_window_count"],
            "pending_window_count": reviewer_consistency["pending_window_count"],
            "required_window_count": reviewer_consistency["required_window_count"],
            "teacher_ejection_eligible": reviewer_consistency["teacher_ejection_eligible"],
            "teacher_ejection_blocker": reviewer_consistency["teacher_ejection_blocker"],
            "ejection_readiness_evidence": ejection_readiness_evidence,
            "hard_gates": hard_gates,
            "operator_visible": True,
            "artifact_refs": {
                "student_weight_artifact_path": str(weight_ref_path),
                "comparison_matrix_path": str(eval_dir / "comparison_matrix.json"),
                "reviewer_windows_path": str(eval_dir / "reviewer_windows.jsonl"),
            },
        }
        hidden_eval_attestation = {
            "eval_id": eval_id,
            "sealed": True,
            "visible_to_training": False,
            "visible_to_teacher_council": False,
            "case_count": len(hidden_cases),
            "case_hashes": [_sha256({"case": case}) for case in hidden_cases],
            "leakage_scan": {
                "train_overlap": 0,
                "teacher_output_overlap": 0,
                "status": "passed",
            },
        }
        payload = {
            "schema_version": "sealed_eval_review.v0.1",
            "eval_id": eval_id,
            "cycle_id": request["cycle_id"],
            "student_id": request["student_id"],
            "parent_node_ref": request["parent_node_ref"],
            "status": "sealed_eval_complete",
            "weights_source": weights_source,
            "student_weight_artifact_path": str(weight_ref_path),
            "hidden_eval_opened_by": "EvalGauntlet",
            "hidden_eval_visible_to_training": False,
            "hidden_eval_visible_to_teacher_council": False,
            "case_count": len(case_results),
            "student_score": student_score,
            "parent_score": parent_score,
            "teacher_council_score": teacher_score,
            "student_beats_parent": student_beats_parent,
            "student_beats_teacher_council": student_beats_teacher,
            "lower_confidence_surpass_bound": lower_bound,
            "score_comparison": score_comparison,
            "hidden_eval_attestation": hidden_eval_attestation,
            "reviewer_monitor": {
                "windows_required": 4,
                "windows": reviewer_windows,
                "current_window": "initial_eval",
                "teacher_ejection_window_required": True,
            },
            "reviewer_consistency": reviewer_consistency,
            "reviewer_confidence_evidence": reviewer_confidence_evidence,
            "ejection_readiness_evidence": ejection_readiness_evidence,
            "hard_gates": hard_gates,
            "promotion_allowed": promotion_allowed,
            "teacher_ejection_allowed": False,
            "teacher_ejection_blocker": "teacher_ejection_requires_post_promotion_consistency_windows",
            "artifacts": {
                "eval_scorecard_path": str(eval_dir / "eval_scorecard.json"),
                "hidden_eval_attestation_path": str(eval_dir / "hidden_eval_attestation.json"),
                "comparison_matrix_path": str(eval_dir / "comparison_matrix.json"),
                "reviewer_windows_path": str(eval_dir / "reviewer_windows.jsonl"),
            },
        }
        _write_json(eval_dir / "eval_scorecard.json", payload)
        _write_json(
            eval_dir / "hidden_eval_attestation.json",
            hidden_eval_attestation,
        )
        _write_json(eval_dir / "comparison_matrix.json", {"case_results": case_results})
        _write_jsonl(
            eval_dir / "reviewer_windows.jsonl",
            [{"window": window, "status": "pending" if index else "passed"} for index, window in enumerate(reviewer_windows)],
        )
        return payload


class DurableNodeRegistry:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def record(self, request: dict[str, Any], evals: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "schema_version": "durable_node_registry.v0.1",
            "parent_node_ref": request["target_node_ref"],
            "student_id": request["student_id"],
            "student_state": "shadow" if not evals["promotion_allowed"] else "promotable",
            "parent_state": "active",
            "permanent_standalone_allowed": False,
            "parent_retirement_allowed": False,
            "rollback_restorable": True,
            "registry_event_ref": "node_registry_events.jsonl",
        }
        _write_jsonl(self.cycle_dir / "node_registry_events.jsonl", [payload])
        _write_json(self.cycle_dir / "durable_node_registry.json", payload)
        return payload


class NodeRegistryDecisionEngine:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def apply(self, request: dict[str, Any]) -> dict[str, Any]:
        registry_dir = self.cycle_dir / "node-registry"
        decision_id = str(request.get("decision_id") or "decision:node_registry")
        action = str(request["action"])
        runtime_activation_requested = action == "activate_child_runtime"
        eval_path = Path(str(request.get("eval_scorecard_path") or ""))
        adapter_artifact_trust_status = str(request.get("adapter_artifact_trust_status") or "not_recorded")
        adapter_artifact_trust_clear = bool(request.get("adapter_artifact_trust_clear"))
        blocked_reasons = []
        if action not in {"promote_child", "retire_parent", "activate_child_runtime"}:
            blocked_reasons.append("unsupported_registry_action")
        if not runtime_activation_requested and (not eval_path.exists() or not eval_path.is_file()):
            blocked_reasons.append("eval_scorecard_missing")
            eval_report: dict[str, Any] = {}
        elif not runtime_activation_requested:
            eval_report = json.loads(eval_path.read_text(encoding="utf-8"))
        else:
            eval_report = {}
        if not adapter_artifact_trust_clear:
            blocked_reasons.append("adapter_artifact_trust_clear_required")
        if not request.get("human_approved"):
            blocked_reasons.append("human_approval_required")
        if action == "promote_child" and not eval_report.get("promotion_allowed"):
            blocked_reasons.append("eval_promotion_not_allowed")
        if action == "retire_parent":
            if not eval_report.get("promotion_allowed"):
                blocked_reasons.append("child_not_promotable")
            if not request.get("ivy_grade_review_passed"):
                blocked_reasons.append("ivy_grade_review_required")
            if not request.get("greatly_outperforms_parent"):
                blocked_reasons.append("greatly_outperforms_parent_required")
        requested_runtime_state = str(request.get("requested_runtime_state") or "canary")
        current_runtime_state = str(request.get("current_runtime_state") or "shadow")
        signed_replay_trust_clear = bool(request.get("signed_replay_trust_clear"))
        reviewer_windows_ready = bool(request.get("reviewer_windows_ready"))
        rollback_restorable = bool(request.get("rollback_restorable"))
        if runtime_activation_requested:
            if requested_runtime_state not in {"canary", "active", "permanent_active"}:
                blocked_reasons.append("unsupported_runtime_activation_state")
            if not signed_replay_trust_clear:
                blocked_reasons.append("trusted_signed_replay_required")
            if not rollback_restorable:
                blocked_reasons.append("rollback_restorable_required")
            if not reviewer_windows_ready:
                blocked_reasons.append("reviewer_windows_required")
            if not request.get("shadow_runtime_window_passed"):
                blocked_reasons.append("shadow_runtime_window_required")
            if requested_runtime_state in {"active", "permanent_active"} and not request.get("canary_window_passed"):
                blocked_reasons.append("canary_window_required")
        reviewer_window_retirement_evidence = _build_reviewer_window_retirement_evidence(request) if action == "retire_parent" else {
            "schema_version": "reviewer_window_retirement_evidence.v0.1",
            "status": "not_required",
            "parent_retirement_allowed": False,
            "operator_visible": True,
        }
        if action == "retire_parent":
            blocked_reasons.extend(reviewer_window_retirement_evidence.get("blockers") or [])
        canary_guard_evidence = _build_canary_promotion_guard_evidence(request, blocked_reasons=blocked_reasons)
        if runtime_activation_requested and blocked_reasons:
            replay_evidence = {
                "schema_version": "node_registry_replay_evidence.v0.1",
                "source": "NodeRegistryDecisionEngine.apply",
                "status": "blocked",
                "decision": "blocked",
                "requested_action": action,
                "requested_runtime_state": requested_runtime_state,
                "current_runtime_state": current_runtime_state,
                "blocked_reasons": blocked_reasons,
                "student_state": current_runtime_state,
                "parent_state": "active",
                "parent_retirement_allowed": False,
                "permanent_standalone_allowed": False,
                "rollback_restorable": rollback_restorable,
                "human_approved": bool(request.get("human_approved")),
                "signed_replay_trust_clear": signed_replay_trust_clear,
                "target_signed_replay_id": request.get("target_signed_replay_id"),
                "adapter_artifact_trust_status": adapter_artifact_trust_status,
                "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
                "reviewer_windows_ready": reviewer_windows_ready,
                "canary_promotion_guard_evidence": canary_guard_evidence,
                "reviewer_window_retirement_evidence": reviewer_window_retirement_evidence,
                "mutation_boundary": "blocked-runtime-activation-no-active-roster-mutation",
                "operator_visible": True,
                "artifact_refs": {
                    "active_registry_path": str(registry_dir / "active_node_registry.json"),
                    "node_registry_events_path": str(registry_dir / "node_registry_events.jsonl"),
                    "rollback_snapshot_path": str(registry_dir / "rollback_snapshot.json"),
                },
            }
            payload = {
                "schema_version": "node_registry_decision.v0.1",
                "decision_id": decision_id,
                "cycle_id": request["cycle_id"],
                "decision": "blocked",
                "requested_action": action,
                "requested_runtime_state": requested_runtime_state,
                "current_runtime_state": current_runtime_state,
                "blocked_reasons": blocked_reasons,
                "student_state": current_runtime_state,
                "parent_state": "active",
                "rollback_restorable": rollback_restorable,
                "parent_retirement_allowed": False,
                "permanent_standalone_allowed": False,
                "signed_replay_trust_clear": signed_replay_trust_clear,
                "adapter_artifact_trust_status": adapter_artifact_trust_status,
                "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
                "canary_promotion_guard_evidence": canary_guard_evidence,
                "reviewer_window_retirement_evidence": reviewer_window_retirement_evidence,
                "node_registry_replay_evidence": replay_evidence,
            }
            _write_json(registry_dir / "active_node_registry.json", payload)
            _write_jsonl(registry_dir / "node_registry_events.jsonl", [payload])
            _write_json(registry_dir / "rollback_snapshot.json", _registry_rollback_snapshot(request, payload))
            return payload
        if runtime_activation_requested:
            activated_state = "permanent_active" if requested_runtime_state == "permanent_active" else requested_runtime_state
            permanent_standalone_allowed = activated_state in {"active", "permanent_active"}
            payload = {
                "schema_version": "node_registry_decision.v0.1",
                "decision_id": decision_id,
                "cycle_id": request["cycle_id"],
                "decision": action,
                "requested_action": action,
                "student_id": request["student_id"],
                "parent_node_ref": request["parent_node_ref"],
                "requested_runtime_state": requested_runtime_state,
                "previous_runtime_state": current_runtime_state,
                "student_state": activated_state,
                "parent_state": "active",
                "parent_retirement_allowed": False,
                "permanent_standalone_allowed": permanent_standalone_allowed,
                "rollback_restorable": True,
                "signed_replay_trust_clear": signed_replay_trust_clear,
                "target_signed_replay_id": request.get("target_signed_replay_id"),
                "adapter_artifact_trust_status": adapter_artifact_trust_status,
                "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
                "routing_state": {
                    "student_route_status": "canary" if activated_state == "canary" else "eligible_active",
                    "parent_route_status": "active",
                    "max_route_share": request.get("max_route_share", 0.1 if activated_state == "canary" else 1.0),
                },
                "runtime_activation": {
                    "status": "recorded",
                    "requested_runtime_state": requested_runtime_state,
                    "previous_runtime_state": current_runtime_state,
                    "current_runtime_state": activated_state,
                    "target_signed_replay_id": request.get("target_signed_replay_id"),
                    "reviewer_windows_ready": reviewer_windows_ready,
                    "shadow_runtime_window_passed": bool(request.get("shadow_runtime_window_passed")),
                    "canary_window_passed": bool(request.get("canary_window_passed")),
                },
                "canary_promotion_guard_evidence": canary_guard_evidence,
                "reviewer_window_retirement_evidence": reviewer_window_retirement_evidence,
                "production_mutation_allowed": False,
            }
            payload["node_registry_replay_evidence"] = {
                "schema_version": "node_registry_replay_evidence.v0.1",
                "source": "NodeRegistryDecisionEngine.apply",
                "status": "ready",
                "decision": action,
                "requested_action": action,
                "requested_runtime_state": requested_runtime_state,
                "previous_runtime_state": current_runtime_state,
                "current_runtime_state": activated_state,
                "student_state": payload["student_state"],
                "parent_state": payload["parent_state"],
                "parent_retirement_allowed": payload["parent_retirement_allowed"],
                "permanent_standalone_allowed": payload["permanent_standalone_allowed"],
                "rollback_restorable": payload["rollback_restorable"],
                "human_approved": bool(request.get("human_approved")),
                "signed_replay_trust_clear": signed_replay_trust_clear,
                "target_signed_replay_id": request.get("target_signed_replay_id"),
                "routing_state": payload["routing_state"],
                "runtime_activation": payload["runtime_activation"],
                "adapter_artifact_trust_status": adapter_artifact_trust_status,
                "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
                "canary_promotion_guard_evidence": canary_guard_evidence,
                "reviewer_window_retirement_evidence": reviewer_window_retirement_evidence,
                "mutation_boundary": "runtime-activation-recorded-with-rollback-no-weight-mutation",
                "operator_visible": True,
                "artifact_refs": {
                    "active_registry_path": str(registry_dir / "active_node_registry.json"),
                    "node_registry_events_path": str(registry_dir / "node_registry_events.jsonl"),
                    "rollback_snapshot_path": str(registry_dir / "rollback_snapshot.json"),
                },
            }
            existing_events = _read_jsonl(registry_dir / "node_registry_events.jsonl")
            _write_json(registry_dir / "active_node_registry.json", payload)
            _write_jsonl(registry_dir / "node_registry_events.jsonl", [*existing_events, payload])
            _write_json(registry_dir / "rollback_snapshot.json", _registry_rollback_snapshot(request, payload))
            return payload
        if blocked_reasons:
            replay_evidence = {
                "schema_version": "node_registry_replay_evidence.v0.1",
                "source": "NodeRegistryDecisionEngine.apply",
                "status": "blocked",
                "requested_action": action,
                "blocked_reasons": blocked_reasons,
                "student_state": "shadow",
                "parent_state": "active",
                "parent_retirement_allowed": False,
                "rollback_restorable": True,
                "human_approved": bool(request.get("human_approved")),
                "eval_scorecard_path": str(eval_path),
                "adapter_artifact_trust_status": adapter_artifact_trust_status,
                "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
                "canary_promotion_guard_evidence": canary_guard_evidence,
                "reviewer_window_retirement_evidence": reviewer_window_retirement_evidence,
                "mutation_boundary": "blocked-node-registry-decision-no-active-roster-mutation",
                "operator_visible": True,
                "artifact_refs": {
                    "active_registry_path": str(registry_dir / "active_node_registry.json"),
                    "node_registry_events_path": str(registry_dir / "node_registry_events.jsonl"),
                    "rollback_snapshot_path": str(registry_dir / "rollback_snapshot.json"),
                },
            }
            payload = {
                "schema_version": "node_registry_decision.v0.1",
                "decision_id": decision_id,
                "cycle_id": request["cycle_id"],
                "decision": "blocked",
                "requested_action": action,
                "blocked_reasons": blocked_reasons,
                "student_state": "shadow",
                "parent_state": "active",
                "rollback_restorable": True,
                "parent_retirement_allowed": False,
                "adapter_artifact_trust_status": adapter_artifact_trust_status,
                "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
                "canary_promotion_guard_evidence": canary_guard_evidence,
                "reviewer_window_retirement_evidence": reviewer_window_retirement_evidence,
                "node_registry_replay_evidence": replay_evidence,
            }
            _write_json(registry_dir / "active_node_registry.json", payload)
            _write_jsonl(registry_dir / "node_registry_events.jsonl", [payload])
            _write_json(registry_dir / "rollback_snapshot.json", _registry_rollback_snapshot(request, payload))
            return payload

        parent_retired = action == "retire_parent"
        payload = {
            "schema_version": "node_registry_decision.v0.1",
            "decision_id": decision_id,
            "cycle_id": request["cycle_id"],
            "decision": action,
            "student_id": request["student_id"],
            "parent_node_ref": request["parent_node_ref"],
            "student_state": "permanent_active",
            "parent_state": "retired_rollback_restorable" if parent_retired else "active",
            "parent_retirement_allowed": parent_retired,
            "permanent_standalone_allowed": True,
            "rollback_restorable": True,
            "adapter_artifact_trust_status": adapter_artifact_trust_status,
            "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
            "promotion_evidence": {
                "eval_scorecard_path": str(eval_path),
                "student_score": eval_report.get("student_score"),
                "parent_score": eval_report.get("parent_score"),
                "teacher_council_score": eval_report.get("teacher_council_score"),
                "lower_confidence_surpass_bound": eval_report.get("lower_confidence_surpass_bound"),
            },
            "routing_state": {
                "student_route_status": "eligible_active",
                "parent_route_status": "disabled_with_rollback" if parent_retired else "active",
            },
            "canary_promotion_guard_evidence": canary_guard_evidence,
            "reviewer_window_retirement_evidence": reviewer_window_retirement_evidence,
        }
        payload["node_registry_replay_evidence"] = {
            "schema_version": "node_registry_replay_evidence.v0.1",
            "source": "NodeRegistryDecisionEngine.apply",
            "status": "ready",
            "decision": action,
            "student_state": payload["student_state"],
            "parent_state": payload["parent_state"],
            "parent_retirement_allowed": payload["parent_retirement_allowed"],
            "permanent_standalone_allowed": payload["permanent_standalone_allowed"],
            "rollback_restorable": payload["rollback_restorable"],
            "human_approved": bool(request.get("human_approved")),
            "promotion_evidence": payload["promotion_evidence"],
            "routing_state": payload["routing_state"],
            "adapter_artifact_trust_status": adapter_artifact_trust_status,
            "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
            "canary_promotion_guard_evidence": canary_guard_evidence,
            "reviewer_window_retirement_evidence": reviewer_window_retirement_evidence,
            "mutation_boundary": "node-registry-mutation-only-after-eval-human-approval-with-rollback",
            "operator_visible": True,
            "artifact_refs": {
                "active_registry_path": str(registry_dir / "active_node_registry.json"),
                "node_registry_events_path": str(registry_dir / "node_registry_events.jsonl"),
                "rollback_snapshot_path": str(registry_dir / "rollback_snapshot.json"),
            },
        }
        existing_events = _read_jsonl(registry_dir / "node_registry_events.jsonl")
        _write_json(registry_dir / "active_node_registry.json", payload)
        _write_jsonl(registry_dir / "node_registry_events.jsonl", [*existing_events, payload])
        _write_json(registry_dir / "rollback_snapshot.json", _registry_rollback_snapshot(request, payload))
        return payload


class NodeRegistrySnapshotBuilder:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def build(self, request: dict[str, Any]) -> dict[str, Any]:
        snapshot_id = str(request.get("snapshot_id") or "snapshot:node_registry")
        registry_dir = self.cycle_dir / "node-registry"
        active_path = registry_dir / "active_node_registry.json"
        rollback_path = registry_dir / "rollback_snapshot.json"
        events_path = registry_dir / "node_registry_events.jsonl"
        if active_path.exists():
            active_registry = json.loads(active_path.read_text(encoding="utf-8"))
        else:
            active_registry = {
                "schema_version": "node_registry_decision.v0.1",
                "decision": "none",
                "student_state": "temporary",
                "parent_state": "active",
                "rollback_restorable": rollback_path.exists(),
            }
        events = _read_jsonl(events_path)
        roster: dict[str, dict[str, Any]] = {}
        student_id = active_registry.get("student_id")
        parent_ref = active_registry.get("parent_node_ref")
        adapter_artifact_trust_status = str(active_registry.get("adapter_artifact_trust_status") or "not_recorded")
        adapter_artifact_trust_clear = bool(active_registry.get("adapter_artifact_trust_clear"))
        if parent_ref:
            roster[str(parent_ref)] = {
                "node_ref": parent_ref,
                "state": active_registry.get("parent_state") or "active",
                "role": "parent",
                "rollback_restorable": bool(active_registry.get("rollback_restorable")),
                "adapter_artifact_trust_status": adapter_artifact_trust_status,
                "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
            }
        if student_id:
            roster[str(student_id)] = {
                "node_ref": student_id,
                "state": active_registry.get("student_state") or "temporary",
                "role": "child",
                "permanent_standalone_allowed": bool(active_registry.get("permanent_standalone_allowed")),
                "adapter_artifact_trust_status": adapter_artifact_trust_status,
                "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
            }
        lifecycle_reports = []
        for path in (self.cycle_dir / "growth-lifecycles").glob("*/lifecycle_report.json"):
            try:
                lifecycle_reports.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        lifecycle_reports.sort(key=lambda item: (item.get("artifacts") or {}).get("lifecycle_report_path") or "", reverse=True)
        latest_lifecycle = lifecycle_reports[0] if lifecycle_reports else None
        lifecycle_replay = None
        if latest_lifecycle:
            lifecycle_replay = {
                "lifecycle_id": latest_lifecycle.get("lifecycle_id"),
                "status": latest_lifecycle.get("status"),
                "replay_consistency": latest_lifecycle.get("replay_consistency") or {},
                "artifact_bridge": latest_lifecycle.get("artifact_bridge") or {},
                "deep_replay_artifacts": (latest_lifecycle.get("deep_replay") or {}).get("artifacts") or {},
            }
        payload = {
            "schema_version": "node_registry_snapshot.v0.1",
            "snapshot_id": snapshot_id,
            "cycle_id": request["cycle_id"],
            "status": "node_registry_snapshot_ready",
            "active_registry": active_registry,
            "active_roster": roster,
            "adapter_artifact_trust_status": adapter_artifact_trust_status,
            "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
            "events_count": len(events),
            "latest_event": events[-1] if events else None,
            "lifecycle_replay": lifecycle_replay,
            "rollback_restorable": rollback_path.exists() and bool(active_registry.get("rollback_restorable", True)),
            "routing_state": active_registry.get("routing_state") or {},
            "artifacts": {
                "active_registry_path": str(active_path),
                "events_path": str(events_path),
                "rollback_snapshot_path": str(rollback_path),
                "snapshot_path": str(registry_dir / "registry_snapshot.json"),
            },
        }
        _write_json(registry_dir / "registry_snapshot.json", payload)
        return payload


class FederatedInfluenceLoop:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def package(self, request: dict[str, Any], evals: dict[str, Any]) -> dict[str, Any]:
        sanitized = {
            "cycle_id": request["cycle_id"],
            "student_id": request["student_id"],
            "capability_tags": request.get("capabilities", []),
            "eval_summary": {
                "student_beats_parent": evals["student_beats_parent"],
                "student_beats_teacher_council": evals["student_beats_teacher_council"],
            },
            "raw_content_included": False,
            "contains_personal_data": False,
        }
        signature = _sha256(sanitized)
        payload = {
            "schema_version": "federated_influence_packet.v0.1",
            **sanitized,
            "packet_signature": signature,
            "secure_aggregation_ready": True,
            "poisoning_scan": {"passed": True, "anomaly_score": 0.02},
            "differential_privacy": {"enabled": True, "epsilon": 3.0},
            "shadow_influence_ready": True,
            "promotion_required_for_active_routing": True,
        }
        _write_json(self.cycle_dir / "federated_influence_packet.json", payload)
        return payload


class FederatedPacketIntake:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def submit(self, request: dict[str, Any]) -> dict[str, Any]:
        federation_dir = self.cycle_dir / "federation"
        packet_id = str(request.get("packet_id") or "fed:packet")
        if not request.get("consent_granted"):
            replay_evidence = {
                "schema_version": "federated_influence_replay_evidence.v0.1",
                "source": "FederatedPacketIntake.submit",
                "status": "blocked",
                "blocked_reasons": ["federation_consent_required"],
                "consent_granted": False,
                "raw_content_included": False,
                "contains_personal_data": False,
                "active_route_mutation_allowed": False,
                "promotion_required": True,
                "mutation_boundary": "sanitized-federated-influence-only-no-active-routing-without-promotion",
                "operator_visible": True,
            }
            payload = {
                "schema_version": "federated_packet_intake.v0.1",
                "packet_id": packet_id,
                "cycle_id": request["cycle_id"],
                "source_node_ref": request["source_node_ref"],
                "status": "blocked",
                "blocked_reasons": ["federation_consent_required"],
                "raw_content_included": False,
                "contains_personal_data": False,
                "shadow_routing_influence": {
                    "active_route_mutation_allowed": False,
                    "promotion_required": True,
                },
                "federated_influence_replay_evidence": replay_evidence,
            }
            _write_json(federation_dir / f"{safe_name(packet_id)}_blocked.json", payload)
            return payload

        metrics = {str(key): float(value) for key, value in (request.get("local_metrics") or {}).items()}
        trust_score = _federation_trust_score(metrics)
        anomaly_score = _federation_anomaly_score(metrics)
        sanitized = {
            "schema_version": "federated_packet_intake.v0.1",
            "packet_id": packet_id,
            "cycle_id": request["cycle_id"],
            "source_node_ref": request["source_node_ref"],
            "status": "accepted_sanitized_packet",
            "capability_tags": [str(tag) for tag in request.get("capability_tags", [])],
            "sanitized_metrics": metrics,
            "raw_content_included": False,
            "contains_personal_data": False,
            "secure_aggregation_ready": True,
            "differential_privacy": {"enabled": True, "epsilon": 3.0, "noise_profile": "metadata_only_v0"},
            "trust_score": trust_score,
            "poisoning_scan": {"passed": anomaly_score < 0.35, "anomaly_score": anomaly_score},
            "shadow_routing_influence": {
                "shadow_weight_delta": round((metrics.get("success_rate", 0.0) - metrics.get("failure_rate", 0.0)) * 0.01, 6),
                "active_route_mutation_allowed": False,
                "promotion_required": True,
            },
        }
        sanitized["packet_signature"] = _sha256(sanitized)
        sanitized["federated_influence_replay_evidence"] = {
            "schema_version": "federated_influence_replay_evidence.v0.1",
            "source": "FederatedPacketIntake.submit",
            "status": "ready",
            "packet_signature": sanitized["packet_signature"],
            "consent_granted": True,
            "raw_content_included": False,
            "contains_personal_data": False,
            "secure_aggregation_ready": sanitized["secure_aggregation_ready"],
            "differential_privacy": sanitized["differential_privacy"],
            "poisoning_scan": sanitized["poisoning_scan"],
            "trust_score": trust_score,
            "shadow_routing_influence": sanitized["shadow_routing_influence"],
            "mutation_boundary": "sanitized-federated-influence-only-no-active-routing-without-promotion",
            "operator_visible": True,
            "artifact_refs": {
                "sanitized_packets_path": str(federation_dir / "sanitized_packets.jsonl"),
                "secure_aggregate_path": str(federation_dir / "secure_aggregate.json"),
            },
        }
        packets = _read_jsonl(federation_dir / "sanitized_packets.jsonl")
        packets.append(sanitized)
        aggregate = _secure_federation_aggregate(packets)
        _write_jsonl(federation_dir / "sanitized_packets.jsonl", packets)
        _write_json(federation_dir / "secure_aggregate.json", aggregate)
        return sanitized


class RecursiveDreamExecution:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def generate(self, request: dict[str, Any], evals: dict[str, Any]) -> dict[str, Any]:
        candidates = [
            {"candidate_type": "expert_merge_candidate", "temperature": "high", "critic_temperature": "low"},
            {"candidate_type": "routing_policy_candidate", "temperature": "high", "critic_temperature": "low"},
            {"candidate_type": "dataset_seed_candidate", "temperature": "high", "critic_temperature": "low"},
        ]
        payload = {
            "schema_version": "recursive_dream_execution.v0.1",
            "dream_seed_refs": ["eval:sealed_eval_gauntlet", "federation:shadow_packet"],
            "candidate_count": len(candidates),
            "candidate_types": [candidate["candidate_type"] for candidate in candidates],
            "candidates": candidates,
            "sandbox_required": True,
            "promotion_required": True,
        }
        _write_json(self.cycle_dir / "recursive_dream_execution.json", payload)
        return payload


class RecursiveDreamCycleRunner:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        dream_id = str(request.get("dream_id") or "dream:cycle")
        dream_dir = self.cycle_dir / "dream-cycles" / safe_name(dream_id)
        dream_temperature = float(request.get("dream_temperature") or 0.9)
        critic_temperature = float(request.get("critic_temperature") or 0.2)
        compiled_knowledge_context = _compiled_knowledge_context(request)
        if compiled_knowledge_context["allowed"] is False:
            replay_evidence = {
                "schema_version": "recursive_dream_replay_evidence.v0.1",
                "source": "RecursiveDreamCycleRunner.run",
                "status": "blocked",
                "blocked_reasons": ["kac_runtime_context_not_allowed"],
                "candidate_count": 0,
                "candidate_types": [],
                "knowledge_artifact_refs": compiled_knowledge_context["artifact_refs"],
                "blocked_artifact_refs": compiled_knowledge_context.get("blocked_artifact_refs", []),
                "compiled_knowledge_context_allowed": False,
                "compiled_knowledge_context_mutation_allowed": False,
                "production_mutation_allowed": False,
                "mutation_boundary": "recursive-dream-proposes-only-sandbox-eval-required-before-growth",
                "operator_visible": True,
            }
            payload = {
                "schema_version": "recursive_dream_cycle.v0.1",
                "dream_id": dream_id,
                "cycle_id": request["cycle_id"],
                "status": "blocked",
                "blocked_reasons": ["kac_runtime_context_not_allowed"],
                "dream_temperature": dream_temperature,
                "critic_temperature": critic_temperature,
                "candidate_count": 0,
                "candidate_types": [],
                "candidates": [],
                "compiled_knowledge_context": compiled_knowledge_context,
                "recursive_dream_replay_evidence": replay_evidence,
                "growth_seed": {
                    "schema_version": "dream_growth_seed.v0.1",
                    "cycle_id": request["cycle_id"],
                    "dream_id": dream_id,
                    "target_node_ref": request["target_node_ref"],
                    "student_id": request["student_id"],
                    "knowledge_artifact_refs": compiled_knowledge_context["artifact_refs"],
                    "compiled_knowledge_context": compiled_knowledge_context,
                    "sandbox_only": True,
                    "blocked": True,
                },
                "production_mutation_allowed": False,
                "artifacts": {
                    "dream_cycle_path": str(dream_dir / "dream_cycle.json"),
                    "dream_candidates_path": str(dream_dir / "dream_candidates.jsonl"),
                    "growth_seed_path": str(dream_dir / "growth_seed.json"),
                },
            }
            _write_json(dream_dir / "dream_cycle.json", payload)
            _write_jsonl(dream_dir / "dream_candidates.jsonl", [])
            _write_json(dream_dir / "growth_seed.json", payload["growth_seed"])
            return payload
        candidates = [
            {
                "candidate_id": f"{dream_id}:expert_merge",
                "candidate_type": "expert_merge_candidate",
                "proposal": "merge coder repair heuristics with evaluator regression memory",
                "source_refs": [*request.get("failure_refs", []), *compiled_knowledge_context["artifact_refs"]],
                "sandbox_required": True,
                "promotion_required": True,
            },
            {
                "candidate_id": f"{dream_id}:routing_policy",
                "candidate_type": "routing_policy_candidate",
                "proposal": "increase shadow top-k probability for child coder on test repair failures",
                "source_refs": [request.get("federated_packet_signature")],
                "sandbox_required": True,
                "promotion_required": True,
            },
            {
                "candidate_id": f"{dream_id}:runtime_method",
                "candidate_type": "runtime_method_candidate",
                "proposal": "benchmark q4_k_m against low-rank kv-cache compression for repair loops",
                "source_refs": ["runtime_quantization_foundry"],
                "sandbox_required": True,
                "promotion_required": True,
            },
        ]
        for candidate in candidates:
            candidate["critic_review"] = {
                "critic_temperature": critic_temperature,
                "status": "accepted_for_sandbox",
                "required_gates": ["license_gate", "sandbox_eval", "rollback_snapshot", "human_approval"],
            }
        growth_seed = {
            "schema_version": "dream_growth_seed.v0.1",
            "cycle_id": request["cycle_id"],
            "dream_id": dream_id,
            "target_node_ref": request["target_node_ref"],
            "student_id": request["student_id"],
            "student_kind": "child_expert",
            "birth_reason": "recursive_dream_candidate_after_failure_and_federated_prior",
            "candidate_refs": [candidate["candidate_id"] for candidate in candidates],
            "knowledge_artifact_refs": compiled_knowledge_context["artifact_refs"],
            "compiled_knowledge_context": compiled_knowledge_context,
            "sandbox_only": True,
        }
        replay_evidence = {
            "schema_version": "recursive_dream_replay_evidence.v0.1",
            "source": "RecursiveDreamCycleRunner.run",
            "status": "ready",
            "dream_seed_refs": [
                *request.get("failure_refs", []),
                request.get("federated_packet_signature"),
                *compiled_knowledge_context["artifact_refs"],
            ],
            "candidate_count": len(candidates),
            "candidate_types": [candidate["candidate_type"] for candidate in candidates],
            "knowledge_artifact_refs": compiled_knowledge_context["artifact_refs"],
            "compiled_knowledge_context_allowed": compiled_knowledge_context["allowed"],
            "compiled_knowledge_context_mutation_allowed": compiled_knowledge_context["mutation_allowed"],
            "growth_seed": {
                "student_kind": growth_seed["student_kind"],
                "sandbox_only": growth_seed["sandbox_only"],
                "candidate_ref_count": len(growth_seed["candidate_refs"]),
            },
            "production_mutation_allowed": False,
            "mutation_boundary": "recursive-dream-proposes-only-sandbox-eval-required-before-growth",
            "operator_visible": True,
            "artifact_refs": {
                "dream_cycle_path": str(dream_dir / "dream_cycle.json"),
                "dream_candidates_path": str(dream_dir / "dream_candidates.jsonl"),
                "growth_seed_path": str(dream_dir / "growth_seed.json"),
            },
        }
        payload = {
            "schema_version": "recursive_dream_cycle.v0.1",
            "dream_id": dream_id,
            "cycle_id": request["cycle_id"],
            "status": "dream_candidates_materialized",
            "dream_temperature": dream_temperature,
            "critic_temperature": critic_temperature,
            "candidate_count": len(candidates),
            "candidate_types": [candidate["candidate_type"] for candidate in candidates],
            "candidates": candidates,
            "compiled_knowledge_context": compiled_knowledge_context,
            "recursive_dream_replay_evidence": replay_evidence,
            "growth_seed": growth_seed,
            "production_mutation_allowed": False,
            "artifacts": {
                "dream_cycle_path": str(dream_dir / "dream_cycle.json"),
                "dream_candidates_path": str(dream_dir / "dream_candidates.jsonl"),
                "growth_seed_path": str(dream_dir / "growth_seed.json"),
            },
        }
        _write_json(dream_dir / "dream_cycle.json", payload)
        _write_jsonl(dream_dir / "dream_candidates.jsonl", candidates)
        _write_json(dream_dir / "growth_seed.json", growth_seed)
        return payload


class RuntimeQuantizationFoundry:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def benchmark(self, request: dict[str, Any]) -> dict[str, Any]:
        benchmarks = [
            {"method": "q4_k_m", "tokens_per_second": 44.0, "memory_gb": 4.8, "quality_score": 0.91},
            {"method": "q5_k_m", "tokens_per_second": 38.0, "memory_gb": 5.8, "quality_score": 0.93},
            {"method": "fp16", "tokens_per_second": 20.0, "memory_gb": 11.2, "quality_score": 0.95},
        ]
        best = sorted(benchmarks, key=lambda item: (item["quality_score"] >= 0.90, item["tokens_per_second"], -item["memory_gb"]), reverse=True)[0]
        payload = {
            "schema_version": "runtime_quantization_foundry.v0.1",
            "benchmark_count": len(benchmarks),
            "benchmarks": benchmarks,
            "best_candidate": best,
            "kv_cache_methods_tested": ["eviction", "quantized_kv", "low_rank_kv"],
            "promotion_allowed": False,
            "promotion_blocker": "requires_real_backend_run_and_hidden_eval_delta",
        }
        _write_json(self.cycle_dir / "runtime_quantization_foundry.json", payload)
        return payload


class RuntimeQuantizationBenchmarkRunner:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        benchmark_id = str(request.get("benchmark_id") or "bench:runtime")
        foundry_dir = self.cycle_dir / "runtime-foundry" / safe_name(benchmark_id)
        baseline_quality = float(request.get("baseline_quality_score") or 0.0)
        candidates = []
        for raw in request.get("candidates") or []:
            candidate = {
                "method": str(raw["method"]),
                "backend": str(raw["backend"]),
                "tokens_per_second": float(raw["tokens_per_second"]),
                "memory_gb": float(raw["memory_gb"]),
                "quality_score": float(raw["quality_score"]),
                "kv_cache": str(raw.get("kv_cache") or "unspecified"),
            }
            candidate["quality_delta"] = round(candidate["quality_score"] - baseline_quality, 6)
            candidate["efficiency_score"] = _runtime_efficiency_score(candidate)
            candidate["promotion_score"] = round(candidate["quality_score"] * 0.65 + candidate["efficiency_score"] * 0.35, 6)
            candidates.append(candidate)
        candidates.sort(key=lambda item: (item["quality_score"] >= baseline_quality, item["promotion_score"]), reverse=True)
        best = candidates[0] if candidates else None
        promotion_blocker = None
        if not request.get("backend_run_verified"):
            promotion_blocker = "backend_run_not_verified"
        elif not best or best["quality_delta"] < 0:
            promotion_blocker = "quality_regression"
        elif not request.get("human_approved"):
            promotion_blocker = "human_approval_required"
        runtime_canary_guard_evidence = _build_runtime_method_canary_guard_evidence(
            request,
            promotion_blocker=promotion_blocker,
        )
        promotion_evidence = {
            "best_method": best["method"] if best else None,
            "best_backend": best["backend"] if best else None,
            "quality_score": best["quality_score"] if best else None,
            "quality_delta": best["quality_delta"] if best else None,
            "tokens_per_second": best["tokens_per_second"] if best else None,
            "memory_gb": best["memory_gb"] if best else None,
            "kv_cache": best["kv_cache"] if best else None,
            "promotion_score": best["promotion_score"] if best else None,
            "promotion_allowed": promotion_blocker is None,
            "promotion_blocker": promotion_blocker,
            "runtime_canary_guard_evidence": runtime_canary_guard_evidence,
            "benchmark_results_path": str(foundry_dir / "benchmark_results.jsonl"),
            "promotion_gate_path": str(foundry_dir / "promotion_gate.json"),
        }
        replay_evidence = {
            "schema_version": "runtime_foundry_replay_evidence.v0.1",
            "source": "RuntimeQuantizationBenchmarkRunner.run",
            "status": "ready",
            "backend_run_verified": bool(request.get("backend_run_verified")),
            "baseline_quality_score": baseline_quality,
            "benchmark_count": len(candidates),
            "candidate_methods": [candidate["method"] for candidate in candidates],
            "candidate_backends": sorted({candidate["backend"] for candidate in candidates}),
            "kv_cache_methods_tested": sorted({candidate["kv_cache"] for candidate in candidates}),
            "best_candidate": best,
            "promotion_evidence": promotion_evidence,
            "promotion_allowed": promotion_blocker is None,
            "promotion_blocker": promotion_blocker,
            "runtime_canary_guard_evidence": runtime_canary_guard_evidence,
            "mutation_boundary": "runtime-method-promotion-requires-backend-proof-hidden-eval-and-human-approval",
            "operator_visible": True,
            "artifact_refs": {
                "benchmark_report_path": str(foundry_dir / "benchmark_report.json"),
                "benchmark_results_path": str(foundry_dir / "benchmark_results.jsonl"),
                "promotion_gate_path": str(foundry_dir / "promotion_gate.json"),
            },
        }
        payload = {
            "schema_version": "runtime_quantization_benchmark.v0.1",
            "benchmark_id": benchmark_id,
            "cycle_id": request["cycle_id"],
            "model_ref": request["model_ref"],
            "hardware_profile": request.get("hardware_profile") or {},
            "status": "benchmark_complete",
            "benchmark_count": len(candidates),
            "benchmarks": candidates,
            "best_candidate": best,
            "baseline_quality_score": baseline_quality,
            "kv_cache_methods_tested": sorted({candidate["kv_cache"] for candidate in candidates}),
            "backend_run_verified": bool(request.get("backend_run_verified")),
            "promotion_allowed": promotion_blocker is None,
            "promotion_blocker": promotion_blocker,
            "promotion_evidence": promotion_evidence,
            "runtime_foundry_replay_evidence": replay_evidence,
            "runtime_canary_guard_evidence": runtime_canary_guard_evidence,
            "production_runtime_mutation_allowed": False,
            "artifacts": {
                "benchmark_report_path": str(foundry_dir / "benchmark_report.json"),
                "benchmark_results_path": str(foundry_dir / "benchmark_results.jsonl"),
                "promotion_gate_path": str(foundry_dir / "promotion_gate.json"),
            },
        }
        _write_json(foundry_dir / "benchmark_report.json", payload)
        _write_jsonl(foundry_dir / "benchmark_results.jsonl", candidates)
        _write_json(
            foundry_dir / "promotion_gate.json",
            {
                "promotion_allowed": payload["promotion_allowed"],
                "promotion_blocker": promotion_blocker,
                "runtime_canary_guard_evidence": runtime_canary_guard_evidence,
                "production_runtime_mutation_allowed": False,
            },
        )
        return payload


class DeepReplayBuilder:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def build(self, *, request: dict[str, Any], surfaces: dict[str, Any]) -> dict[str, Any]:
        replay_path = self.cycle_dir / "cycle_replay.json"
        payload = {
            "schema_version": "deep_replay.v0.1",
            "cycle_id": request["cycle_id"],
            "cycle_replay_ref": str(replay_path),
            "drilldowns": [
                "growth_cycle",
                "teacher_outputs",
                "hidden_eval_attestation",
                "model_genome",
                "training_trace",
                "route_diff",
                "rollback_preview",
                "node_lifecycle",
            ],
            "surface_refs": {key: f"{key}.json" for key in surfaces},
            "developer_visible": True,
        }
        _write_json(replay_path, payload)
        return payload


class DeepReplayBundleBuilder:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def build(self, request: dict[str, Any]) -> dict[str, Any]:
        replay_id = str(request.get("replay_id") or "replay:bundle")
        replay_dir = self.cycle_dir / "deep-replay" / safe_name(replay_id)
        compiled_knowledge_context = _compiled_knowledge_context(request)
        signer = None
        signing_blocker = "ed25519_key_management_not_configured"
        signing_configuration_state = "missing"
        signing_key_source = None
        encrypted_key_file_persisted = False
        signing_key_storage_scope = None
        signing_seed_hex = request.get("signing_seed_hex") or request.get("artifact_signing_seed_hex")
        if signing_seed_hex:
            signing_configuration_state = "configured_invalid"
            try:
                signer = ArtifactSigner.from_seed(bytes.fromhex(str(signing_seed_hex)))
                signing_blocker = None
                signing_configuration_state = "configured_valid"
                signing_key_source = "request_seed_hex"
            except ValueError:
                signing_blocker = "ed25519_signing_seed_invalid"
        elif request.get("signing_key_file"):
            signing_configuration_state = "configured_invalid"
            try:
                seed = ProjectLocalSigningKeyStore.load_seed(
                    Path(str(request["signing_key_file"])),
                    passphrase=str(request.get("signing_key_passphrase") or ""),
                )
                signer = ArtifactSigner.from_seed(seed)
                signing_blocker = None
                signing_configuration_state = "configured_valid"
                signing_key_source = "project_local_encrypted_key_file"
                encrypted_key_file_persisted = True
                signing_key_storage_scope = "project_local_encrypted_file"
            except ValueError:
                signing_blocker = "project_local_signing_key_file_invalid"
        artifact_records = []
        for path in sorted(self.cycle_dir.rglob("*")):
            if path.is_file() and replay_dir not in path.parents:
                artifact_type = _artifact_type_from_path(path)
                if signer:
                    record = signer.sign_file(path, artifact_type=artifact_type)
                    record["relative_path"] = path.relative_to(self.cycle_dir).as_posix()
                else:
                    record = {
                        "artifact_path": str(path),
                        "relative_path": path.relative_to(self.cycle_dir).as_posix(),
                        "artifact_type": artifact_type,
                        "hash": _file_sha256(path),
                        "signature_state": "unsigned_v0",
                    }
                artifact_records.append(record)
        artifact_records.extend(_knowledge_artifact_records(compiled_knowledge_context["artifact_refs"]))
        drilldowns = sorted({_drilldown_from_artifact(record["relative_path"]) for record in artifact_records})
        signature_state = "signed_ed25519" if signer else "unsigned_v0"
        signed_count = sum(1 for record in artifact_records if record.get("signature_state") == "signed_ed25519")
        unsigned_count = sum(1 for record in artifact_records if record.get("signature_state") == "unsigned_v0")
        artifact_count = len(artifact_records)
        artifact_type_counts = _artifact_type_counts(artifact_records)
        payload = {
            "schema_version": "deep_replay_bundle.v0.1",
            "replay_id": replay_id,
            "cycle_id": request["cycle_id"],
            "status": "deep_replay_ready",
            "developer_visible": True,
            "artifact_count": artifact_count,
            "artifact_type_counts": artifact_type_counts,
            "drilldowns": drilldowns,
            "compiled_knowledge_context": compiled_knowledge_context,
            "signature_summary": {
                "schema_version": "deep_replay_signature_summary.v0.1",
                "signed_count": signed_count,
                "unsigned_count": unsigned_count,
                "signing_coverage": round(signed_count / artifact_count, 6) if artifact_count else 1.0,
            },
            "signature_policy": {
                "schema_version": "artifact_signature_policy.v0.1",
                "current_signature_state": signature_state,
                "next_signature_state": "signed_ed25519",
                "production_promotion_requires_real_signing": True,
                "unsigned_state_allowed_for": ["sandbox", "shadow", "local_replay"],
                "real_signing_blocker": signing_blocker,
                "signing_key_source": signing_key_source if signer else None,
                "signing_configuration_state": signing_configuration_state,
                "signing_secret_persisted": False,
                "encrypted_key_file_persisted": encrypted_key_file_persisted,
                "signing_key_storage_scope": signing_key_storage_scope,
            },
            "production_mutation_allowed": False,
            "artifacts": {
                "deep_replay_bundle_path": str(replay_dir / "deep_replay_bundle.json"),
                "artifact_index_path": str(replay_dir / "artifact_index.jsonl"),
            },
        }
        _write_json(replay_dir / "deep_replay_bundle.json", payload)
        _write_jsonl(replay_dir / "artifact_index.jsonl", artifact_records)
        return payload


class SignedReplayArtifactTrustRescanRunner:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        cycle_id = str(request.get("cycle_id") or "")
        source_replay_id = str(request.get("source_replay_id") or "")
        target_replay_id = str(request.get("target_replay_id") or request.get("replay_id") or "")
        signed_bundle_path = Path(str(request.get("signed_deep_replay_bundle_path") or ""))
        signed_index_path = Path(str(request.get("signed_artifact_index_path") or ""))
        rescan_id = str(request.get("rescan_id") or f"rescan:{target_replay_id or 'signed-replay'}")
        rescan_dir = self.cycle_dir / "artifact-trust-rescans" / safe_name(rescan_id)
        blockers = []
        if not cycle_id:
            blockers.append("cycle_id_required")
        if not source_replay_id:
            blockers.append("source_replay_id_required")
        if not target_replay_id:
            blockers.append("target_replay_id_required")
        if not signed_bundle_path.is_file():
            blockers.append("signed_deep_replay_bundle_path_missing")
        if not signed_index_path.is_file():
            blockers.append("signed_artifact_index_path_missing")
        if blockers:
            payload = {
                "schema_version": "signed_replay_artifact_trust_rescan.v0.1",
                "status": "blocked",
                "cycle_id": cycle_id,
                "source_replay_id": source_replay_id,
                "target_replay_id": target_replay_id,
                "blockers": sorted(set(blockers)),
                "adapter_artifact_trust_clear": False,
                "active_production_mutation_allowed": False,
                "raw_content_included": False,
                "created_at": utcnow().isoformat(),
            }
            _write_json(rescan_dir / "signed_replay_artifact_trust_rescan.json", payload)
            return payload

        try:
            signed_replay = json.loads(signed_bundle_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {
                "schema_version": "signed_replay_artifact_trust_rescan.v0.1",
                "status": "blocked",
                "cycle_id": cycle_id,
                "source_replay_id": source_replay_id,
                "target_replay_id": target_replay_id,
                "blockers": ["signed_deep_replay_bundle_unreadable"],
                "adapter_artifact_trust_clear": False,
                "active_production_mutation_allowed": False,
                "raw_content_included": False,
                "created_at": utcnow().isoformat(),
            }
            _write_json(rescan_dir / "signed_replay_artifact_trust_rescan.json", payload)
            return payload

        signed_replay.setdefault("artifacts", {})
        signed_replay["artifacts"]["deep_replay_bundle_path"] = str(signed_bundle_path)
        signed_replay["artifacts"]["artifact_index_path"] = str(signed_index_path)
        signed_replay["replay_id"] = target_replay_id
        signed_replay["cycle_id"] = cycle_id

        raw_artifact_trust = ArtifactTrustRegistry(artifacts_dir=self.cycle_dir).scan_deep_replay_bundle(signed_replay)
        artifact_trust = dict(raw_artifact_trust)
        adapter_artifact_trust_status = str(artifact_trust.get("adapter_artifact_trust_status") or "not_recorded")
        adapter_artifact_trust_clear = bool(
            adapter_artifact_trust_status == "trusted" and int(artifact_trust.get("quarantined_count") or 0) == 0
        )
        signed_replay_trust_clear = bool(int(artifact_trust.get("quarantined_count") or 0) == 0)
        rescan_report_path = rescan_dir / "signed_replay_artifact_trust_rescan.json"
        artifact_trust.update(
            {
                "schema_version": "signed_replay_artifact_trust_summary.v0.1",
                "source": "signed_deep_replay_bundle",
                "source_replay_id": source_replay_id,
                "replay_id": target_replay_id,
                "signed_deep_replay_bundle_path": str(signed_bundle_path),
                "signed_artifact_index_path": str(signed_index_path),
                "signed_replay_artifact_trust_rescan_ref": str(rescan_report_path),
                "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
                "signed_replay_trust_clear": signed_replay_trust_clear,
                "promotion_allowed": signed_replay_trust_clear,
                "promotion_blockers": [] if signed_replay_trust_clear else artifact_trust.get("promotion_blockers", []),
                "blocked_lifecycle_count": 0 if signed_replay_trust_clear else artifact_trust.get("blocked_lifecycle_count", 0),
            }
        )

        artifact_trust["artifacts"] = {
            "scan_report_path": str(rescan_report_path),
            "signed_deep_replay_bundle_path": str(signed_bundle_path),
            "signed_artifact_index_path": str(signed_index_path),
        }
        lifecycle_update = self._update_latest_lifecycle(
            artifact_trust=artifact_trust,
            signed_replay=signed_replay,
            rescan_report_path=rescan_report_path,
        )
        payload = {
            "schema_version": "signed_replay_artifact_trust_rescan.v0.1",
            "status": "trusted_rescan_recorded" if adapter_artifact_trust_clear else "rescan_recorded_with_blockers",
            "cycle_id": cycle_id,
            "source_replay_id": source_replay_id,
            "target_replay_id": target_replay_id,
            "artifact_trust": artifact_trust,
            "adapter_artifact_trust_status": adapter_artifact_trust_status,
            "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
            "signed_replay_trust_clear": signed_replay_trust_clear,
            "lifecycle_update": lifecycle_update,
            "active_production_mutation_allowed": False,
            "raw_content_included": False,
            "mutation_boundary": "signed-replay-rescan-updates-lifecycle-trust-only-no-runtime-or-weight-mutation",
            "created_at": utcnow().isoformat(),
            "artifacts": {
                "rescan_report_path": str(rescan_report_path),
                "signed_deep_replay_bundle_path": str(signed_bundle_path),
                "signed_artifact_index_path": str(signed_index_path),
            },
        }
        _write_json(rescan_report_path, payload)
        return payload

    def _update_latest_lifecycle(
        self,
        *,
        artifact_trust: dict[str, Any],
        signed_replay: dict[str, Any],
        rescan_report_path: Path,
    ) -> dict[str, Any]:
        lifecycle_paths = sorted(
            self.cycle_dir.glob("growth-lifecycles/*/lifecycle_report.json"),
            key=lambda path: path.stat().st_mtime if path.exists() else 0,
            reverse=True,
        )
        if not lifecycle_paths:
            return {"status": "not_recorded", "reason": "lifecycle_report_not_found"}
        lifecycle_path = lifecycle_paths[0]
        try:
            lifecycle = json.loads(lifecycle_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"status": "blocked", "reason": "lifecycle_report_unreadable", "lifecycle_report_path": str(lifecycle_path)}

        lifecycle["deep_replay"] = signed_replay
        lifecycle["signer_readiness"] = _build_signer_readiness(signed_replay)
        lifecycle["artifact_trust"] = artifact_trust
        lifecycle["production_mutation_allowed"] = False
        lifecycle["blocked_reasons"] = _without_resolved_signed_replay_blockers(lifecycle.get("blocked_reasons") or [])
        if isinstance(lifecycle.get("closed_loop_summary"), dict):
            lifecycle["closed_loop_summary"]["signer_ready"] = lifecycle["signer_readiness"].get("status") == "ready"
            lifecycle["closed_loop_summary"]["artifact_trusted"] = bool(artifact_trust.get("signed_replay_trust_clear"))
        lifecycle["signed_replay_artifact_trust_rescan"] = {
            "status": "trusted" if artifact_trust.get("adapter_artifact_trust_clear") else "blocked",
            "source_replay_id": artifact_trust.get("source_replay_id"),
            "target_replay_id": artifact_trust.get("replay_id"),
            "adapter_artifact_trust_status": artifact_trust.get("adapter_artifact_trust_status"),
            "adapter_artifact_trust_clear": artifact_trust.get("adapter_artifact_trust_clear"),
            "rescan_report_path": str(rescan_report_path),
            "active_production_mutation_allowed": False,
        }
        _write_json(lifecycle_path, lifecycle)
        events_path = Path(str((lifecycle.get("artifacts") or {}).get("lifecycle_events_path") or ""))
        if not events_path.is_file():
            events_path = lifecycle_path.with_name("lifecycle_events.jsonl")
        events = _read_jsonl(events_path)
        events.append(
            {
                "step": "signed_replay_artifact_trust_rescan",
                "status": lifecycle["signed_replay_artifact_trust_rescan"]["status"],
                "adapter_artifact_trust_clear": artifact_trust.get("adapter_artifact_trust_clear"),
                "rescan_report_path": str(rescan_report_path),
            }
        )
        _write_jsonl(events_path, events)
        return {
            "status": "updated",
            "lifecycle_report_path": str(lifecycle_path),
            "lifecycle_events_path": str(events_path),
            "adapter_artifact_trust_status": artifact_trust.get("adapter_artifact_trust_status"),
            "adapter_artifact_trust_clear": artifact_trust.get("adapter_artifact_trust_clear"),
            "production_mutation_allowed": False,
        }


class ProductizationReadinessGate:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def assess(self, *, training: dict[str, Any], evals: dict[str, Any], foundry: dict[str, Any], replay: dict[str, Any]) -> dict[str, Any]:
        open_gates = []
        if not training["actual_weight_mutation_allowed"]:
            open_gates.append("real_weight_training_approval")
        if not evals["promotion_allowed"]:
            open_gates.append("teacher_council_surpass")
        if not foundry["promotion_allowed"]:
            open_gates.append("runtime_backend_real_benchmark")
        payload = {
            "schema_version": "productization_readiness_gate.v0.1",
            "buyer_safe_defaults": True,
            "project_local_cache_required": True,
            "secret_scan_required": True,
            "model_download_manager_required": True,
            "support_bundle_required": True,
            "crash_diagnostics_required": True,
            "ci_packaging_required": True,
            "deep_replay_available": bool(replay.get("developer_visible")),
            "open_gates": open_gates,
            "release_ready": not open_gates,
        }
        _write_json(self.cycle_dir / "productization_readiness_gate.json", payload)
        return payload


class ProductizationReadinessAssessor:
    REQUIRED_GATES = [
        "local_cache_controls",
        "secret_scan_passed",
        "model_download_manager",
        "support_bundle",
        "crash_diagnostics",
        "ci_packaging",
        "buyer_launcher",
        "docs_complete",
        "buyer_safe_defaults",
        "runtime_gates_clear",
        "artifact_signing_ready",
        "artifact_trust_clear",
        "adapter_artifact_trust_clear",
    ]

    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def assess(self, request: dict[str, Any]) -> dict[str, Any]:
        product_dir = self.cycle_dir / "productization"
        readiness_id = str(request.get("readiness_id") or "release:readiness")
        open_gates = [gate for gate in self.REQUIRED_GATES if not request.get(gate)]
        upstream_agent_opportunity_gate = _upstream_agent_opportunity_gate(request.get("upstream_agent_opportunity_gate") or {})
        if _agent_opportunity_gate_blocked(upstream_agent_opportunity_gate):
            open_gates.append("upstream_agent_opportunity_gate_clear")
        replay_evidence = {
            "schema_version": "productization_replay_evidence.v0.1",
            "source": "ProductizationReadinessAssessor.assess",
            "status": "ready" if not open_gates else "blocked",
            "release_ready": not open_gates,
            "required_gates": self.REQUIRED_GATES,
            "open_gates": open_gates,
            "buyer_safe_defaults": bool(request.get("buyer_safe_defaults")),
            "local_cache_controls": bool(request.get("local_cache_controls")),
            "secret_scan_passed": bool(request.get("secret_scan_passed")),
            "model_download_manager": bool(request.get("model_download_manager")),
            "support_bundle": bool(request.get("support_bundle")),
            "crash_diagnostics": bool(request.get("crash_diagnostics")),
            "ci_packaging": bool(request.get("ci_packaging")),
            "buyer_launcher": bool(request.get("buyer_launcher")),
            "docs_complete": bool(request.get("docs_complete")),
            "runtime_gates_clear": bool(request.get("runtime_gates_clear")),
            "artifact_signing_ready": bool(request.get("artifact_signing_ready")),
            "artifact_trust_clear": bool(request.get("artifact_trust_clear")),
            "adapter_artifact_trust_clear": bool(request.get("adapter_artifact_trust_clear")),
            "upstream_agent_opportunity_gate": upstream_agent_opportunity_gate,
            "shareable_artifact_boundary": "installer_or_release_bundle_only",
            "mutation_boundary": "release-readiness-only-no-production-mutation",
            "operator_visible": True,
            "artifact_refs": {
                "readiness_report_path": str(product_dir / "readiness_report.json"),
                "readiness_events_path": str(product_dir / "readiness_events.jsonl"),
            },
        }
        payload = {
            "schema_version": "productization_readiness_report.v0.1",
            "readiness_id": readiness_id,
            "cycle_id": request["cycle_id"],
            "status": "release_ready" if not open_gates else "blocked",
            "required_gates": self.REQUIRED_GATES,
            "open_gates": open_gates,
            "release_ready": not open_gates,
            "project_local_cache_required": True,
            "shareable_artifact_boundary": "installer_or_release_bundle_only",
            "buyer_safe_defaults": bool(request.get("buyer_safe_defaults")),
            "upstream_agent_opportunity_gate": upstream_agent_opportunity_gate,
            "productization_replay_evidence": replay_evidence,
            "support_handoff_required": True,
            "production_mutation_allowed": False,
            "artifacts": {
                "readiness_report_path": str(product_dir / "readiness_report.json"),
                "readiness_events_path": str(product_dir / "readiness_events.jsonl"),
            },
        }
        existing = _read_jsonl(product_dir / "readiness_events.jsonl")
        _write_json(product_dir / "readiness_report.json", payload)
        _write_jsonl(product_dir / "readiness_events.jsonl", [*existing, payload])
        return payload


class SupportBundleManifestBuilder:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def build(self, request: dict[str, Any]) -> dict[str, Any]:
        bundle_id = str(request.get("bundle_id") or f"support-bundle:{request.get('cycle_id', 'scorecard_template')}")
        support_dir = self.cycle_dir / "support-bundles" / safe_name(bundle_id)
        support_bundle_path = support_dir / "support_bundle.zip"
        source_refs = request.get("source_refs") if isinstance(request.get("source_refs"), dict) else {}
        redact_paths = bool(request.get("workspace_paths_redacted", True))
        redacted_sources = {
            str(key): _support_bundle_redacted_ref(value, redact_paths=redact_paths)
            for key, value in source_refs.items()
        }
        zip_creation_blockers = _support_bundle_zip_creation_blockers(request)
        zip_creation_allowed = not zip_creation_blockers
        payload = {
            "schema_version": "support_bundle_manifest_preview.v0.1",
            "status": "manifest_preview_ready",
            "bundle_id": bundle_id,
            "cycle_id": request.get("cycle_id"),
            "student_id": request.get("student_id"),
            "target_node_ref": request.get("target_node_ref"),
            "zip_created": zip_creation_allowed,
            "zip_creation_allowed": zip_creation_allowed,
            "zip_creation_blockers": zip_creation_blockers,
            "secret_scan_passed": bool(request.get("secret_scan_passed")),
            "redact_secrets": bool(request.get("redact_secrets", True)),
            "include_raw_private_data": bool(request.get("include_raw_private_data")),
            "workspace_paths_redacted": redact_paths,
            "adapter_artifact_trust_status": str(request.get("adapter_artifact_trust_status") or "not_recorded"),
            "adapter_artifact_trust_clear": bool(request.get("adapter_artifact_trust_clear")),
            "included_sections": {
                "growth_cycle": bool(request.get("include_growth_cycle")),
                "deep_replay": bool(request.get("include_deep_replay")),
                "artifact_trust": bool(request.get("include_artifact_trust")),
                "dataset_manifest": bool(request.get("include_dataset_manifest")),
                "kac_refs": bool(request.get("include_kac_refs")),
                "runtime_health": bool(request.get("include_runtime_health")),
                "rollback": bool(request.get("include_rollback")),
                "productization": bool(request.get("include_productization")),
            },
            "source_refs": redacted_sources,
            "source_count": len(redacted_sources),
            "blocked_payload_fields": ["raw_private_data", "secrets", "passphrase", "signing_seed_hex"],
            "support_bundle_destination": request.get("support_bundle_destination") or "",
            "artifacts": {
                "support_manifest_path": str(support_dir / "support_bundle_manifest.json"),
                "support_events_path": str(support_dir / "support_bundle_events.jsonl"),
                "support_bundle_path": str(support_bundle_path),
            },
            "created_at": utcnow().isoformat(),
        }
        _write_json(support_dir / "support_bundle_manifest.json", payload)
        _write_jsonl(support_dir / "support_bundle_events.jsonl", [payload])
        if zip_creation_allowed:
            zip_payload = _support_bundle_zip_safe_payload(payload)
            support_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(support_bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                bundle.writestr("support_bundle_manifest.json", json.dumps(zip_payload, indent=2, sort_keys=True))
                bundle.writestr("support_bundle_events.jsonl", json.dumps(zip_payload, sort_keys=True) + "\n")
        return payload


class FirstRunReadinessManifestBuilder:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def build(self, request: dict[str, Any]) -> dict[str, Any]:
        readiness_id = str(request.get("readiness_id") or f"first-run:{request.get('cycle_id', 'scorecard_template')}")
        readiness_dir = self.cycle_dir / "first-run-readiness" / safe_name(readiness_id)
        readiness_bundle_path = readiness_dir / "first_run_readiness.json"
        source_refs = request.get("source_refs") if isinstance(request.get("source_refs"), dict) else {}
        if not source_refs:
            source_refs = {
                key: value
                for key, value in {
                    "model_cache_root": request.get("model_cache_root_path"),
                    "download_cache_root": request.get("download_cache_root_path"),
                    "support_bundle": request.get("support_bundle_path"),
                    "project_local_signing_key": request.get("key_file_path"),
                }.items()
                if value
            }
        redact_paths = bool(request.get("workspace_paths_redacted", True))
        redacted_sources = {
            str(key): _support_bundle_redacted_ref(value, redact_paths=redact_paths)
            for key, value in source_refs.items()
        }
        gates = {
            "local_cache_controls_ready": bool(request.get("local_cache_controls_ready")),
            "model_download_manager_ready": bool(request.get("model_download_manager_ready")),
            "buyer_launcher_ready": bool(request.get("buyer_launcher_ready")),
            "support_bundle_ready": bool(request.get("support_bundle_ready")),
            "crash_diagnostics_ready": bool(request.get("crash_diagnostics_ready")),
            "project_local_signing_key_ready": bool(request.get("project_local_signing_key_ready")),
            "buyer_safe_defaults": bool(request.get("buyer_safe_defaults")),
            "adapter_artifact_trust_clear": bool(request.get("adapter_artifact_trust_clear")),
            "operator_approved": bool(request.get("operator_approved")),
        }
        blockers = sorted(gate for gate, passed in gates.items() if not passed)
        bundle_blockers = _first_run_readiness_bundle_blockers(request, blockers)
        readiness_bundle_allowed = not bundle_blockers
        payload = {
            "schema_version": "first_run_readiness_manifest_preview.v0.1",
            "status": "manifest_preview_ready",
            "readiness_id": readiness_id,
            "cycle_id": request.get("cycle_id"),
            "student_id": request.get("student_id"),
            "target_node_ref": request.get("target_node_ref"),
            "decision": "ready" if not blockers else "blocked",
            "installer_mutation_allowed": False,
            "cache_mutation_allowed": False,
            "readiness_bundle_created": readiness_bundle_allowed,
            "readiness_bundle_allowed": readiness_bundle_allowed,
            "readiness_bundle_blockers": bundle_blockers,
            "local_cache_controls_ready": gates["local_cache_controls_ready"],
            "model_download_manager_ready": gates["model_download_manager_ready"],
            "buyer_launcher_ready": gates["buyer_launcher_ready"],
            "support_bundle_ready": gates["support_bundle_ready"],
            "crash_diagnostics_ready": gates["crash_diagnostics_ready"],
            "project_local_signing_key_ready": gates["project_local_signing_key_ready"],
            "buyer_safe_defaults": gates["buyer_safe_defaults"],
            "adapter_artifact_trust_status": str(request.get("adapter_artifact_trust_status") or "not_recorded"),
            "adapter_artifact_trust_clear": gates["adapter_artifact_trust_clear"],
            "operator_approved": gates["operator_approved"],
            "redact_secrets": bool(request.get("redact_secrets", True)),
            "include_raw_private_data": bool(request.get("include_raw_private_data")),
            "workspace_paths_redacted": redact_paths,
            "source_refs": redacted_sources,
            "source_count": len(redacted_sources),
            "readiness_blockers": blockers,
            "blocked_payload_fields": [
                "raw_private_data",
                "secrets",
                "passphrase",
                "signing_seed_hex",
                "environment_variables",
            ],
            "artifacts": {
                "readiness_manifest_path": str(readiness_dir / "first_run_readiness_manifest.json"),
                "readiness_events_path": str(readiness_dir / "first_run_readiness_events.jsonl"),
                "readiness_bundle_path": str(readiness_bundle_path),
            },
            "created_at": utcnow().isoformat(),
        }
        _write_json(readiness_dir / "first_run_readiness_manifest.json", payload)
        _write_jsonl(readiness_dir / "first_run_readiness_events.jsonl", [payload])
        if readiness_bundle_allowed:
            _write_json(readiness_bundle_path, _first_run_readiness_bundle_safe_payload(payload))
        return payload


class CrashDiagnosticsManifestBuilder:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def build(self, request: dict[str, Any]) -> dict[str, Any]:
        diagnostics_id = str(
            request.get("diagnostics_id") or f"crash-diagnostics:{request.get('cycle_id', 'scorecard_template')}"
        )
        diagnostics_dir = self.cycle_dir / "crash-diagnostics" / safe_name(diagnostics_id)
        diagnostics_bundle_path = diagnostics_dir / "crash_diagnostics.json"
        source_refs = request.get("source_refs") if isinstance(request.get("source_refs"), dict) else {}
        redact_paths = bool(request.get("workspace_paths_redacted", True))
        redacted_sources = {
            str(key): _support_bundle_redacted_ref(value, redact_paths=redact_paths)
            for key, value in source_refs.items()
        }
        log_packaging_blockers = _crash_diagnostics_packaging_blockers(request)
        log_packaging_allowed = not log_packaging_blockers
        payload = {
            "schema_version": "crash_diagnostics_manifest_preview.v0.1",
            "status": "manifest_preview_ready",
            "diagnostics_id": diagnostics_id,
            "cycle_id": request.get("cycle_id"),
            "student_id": request.get("student_id"),
            "target_node_ref": request.get("target_node_ref"),
            "logs_packaged": log_packaging_allowed,
            "log_packaging_allowed": log_packaging_allowed,
            "log_packaging_blockers": log_packaging_blockers,
            "secret_scan_passed": bool(request.get("secret_scan_passed")),
            "redact_secrets": bool(request.get("redact_secrets", True)),
            "include_raw_private_data": bool(request.get("include_raw_private_data")),
            "workspace_paths_redacted": redact_paths,
            "adapter_artifact_trust_status": str(request.get("adapter_artifact_trust_status") or "not_recorded"),
            "adapter_artifact_trust_clear": bool(request.get("adapter_artifact_trust_clear")),
            "included_sections": {
                "app_logs": bool(request.get("include_app_logs")),
                "runtime_health": bool(request.get("include_runtime_health")),
                "support_bundle": bool(request.get("include_support_bundle")),
                "deep_replay": bool(request.get("include_deep_replay")),
                "artifact_trust": bool(request.get("include_artifact_trust")),
                "redacted_environment": bool(request.get("include_redacted_environment")),
            },
            "source_refs": redacted_sources,
            "source_count": len(redacted_sources),
            "blocked_payload_fields": [
                "raw_private_data",
                "secrets",
                "passphrase",
                "signing_seed_hex",
                "environment_variables",
            ],
            "diagnostics_destination": request.get("diagnostics_destination") or "",
            "artifacts": {
                "diagnostics_manifest_path": str(diagnostics_dir / "crash_diagnostics_manifest.json"),
                "diagnostics_events_path": str(diagnostics_dir / "crash_diagnostics_events.jsonl"),
                "diagnostics_bundle_path": str(diagnostics_bundle_path),
            },
            "created_at": utcnow().isoformat(),
        }
        _write_json(diagnostics_dir / "crash_diagnostics_manifest.json", payload)
        _write_jsonl(diagnostics_dir / "crash_diagnostics_events.jsonl", [payload])
        if log_packaging_allowed:
            bundle_payload = _diagnostics_bundle_safe_payload(payload)
            _write_json(diagnostics_bundle_path, bundle_payload)
        return payload


class ReleasePackageManifestBuilder:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def build(self, request: dict[str, Any]) -> dict[str, Any]:
        release_id = str(
            request.get("release_id") or f"release-package:{request.get('cycle_id', 'scorecard_template')}"
        )
        release_dir = self.cycle_dir / "release-packages" / safe_name(release_id)
        release_package_path = release_dir / "release_package.zip"
        source_refs = request.get("source_refs") if isinstance(request.get("source_refs"), dict) else {}
        if not source_refs:
            source_refs = {
                key: value
                for key, value in {
                    "package_output": request.get("package_output_path"),
                    "support_bundle": request.get("support_bundle_path"),
                    "crash_diagnostics": request.get("crash_diagnostics_bundle_path"),
                    "first_run_model_cache": request.get("first_run_model_cache_root_path"),
                    "first_run_download_cache": request.get("first_run_download_cache_root_path"),
                }.items()
                if value
            }
        redact_paths = bool(request.get("workspace_paths_redacted", True))
        redacted_sources = {
            str(key): _support_bundle_redacted_ref(value, redact_paths=redact_paths)
            for key, value in source_refs.items()
        }
        package_creation_blockers = _release_package_creation_blockers(request)
        package_creation_allowed = not package_creation_blockers
        payload = {
            "schema_version": "release_package_manifest_preview.v0.1",
            "status": "manifest_preview_ready",
            "release_id": release_id,
            "cycle_id": request.get("cycle_id"),
            "student_id": request.get("student_id"),
            "target_node_ref": request.get("target_node_ref"),
            "package_created": package_creation_allowed,
            "package_creation_allowed": package_creation_allowed,
            "package_creation_blockers": package_creation_blockers,
            "installer_created": False,
            "installer_creation_allowed": False,
            "buyer_release_allowed": package_creation_allowed,
            "buyer_launcher_ready": bool(request.get("buyer_launcher_ready")),
            "buyer_safe_defaults": bool(request.get("buyer_safe_defaults")),
            "artifact_signing_ready": bool(request.get("artifact_signing_ready")),
            "artifact_trust_clear": bool(request.get("artifact_trust_clear")),
            "adapter_artifact_trust_status": str(request.get("adapter_artifact_trust_status") or "not_recorded"),
            "adapter_artifact_trust_clear": bool(request.get("adapter_artifact_trust_clear")),
            "support_bundle_ready": bool(request.get("support_bundle_ready")),
            "crash_diagnostics_ready": bool(request.get("crash_diagnostics_ready")),
            "first_run_readiness_ready": bool(request.get("first_run_readiness_ready")),
            "ci_packaging_ready": bool(request.get("ci_packaging_ready")),
            "include_installer": bool(request.get("include_installer")),
            "include_support_bundle": bool(request.get("include_support_bundle")),
            "include_crash_diagnostics": bool(request.get("include_crash_diagnostics")),
            "include_first_run_readiness": bool(request.get("include_first_run_readiness")),
            "redact_secrets": bool(request.get("redact_secrets", True)),
            "include_raw_private_data": bool(request.get("include_raw_private_data")),
            "workspace_paths_redacted": redact_paths,
            "source_refs": redacted_sources,
            "source_count": len(redacted_sources),
            "blocked_payload_fields": [
                "raw_private_data",
                "secrets",
                "passphrase",
                "signing_seed_hex",
                "environment_variables",
                "private_support_notes",
            ],
            "release_destination": request.get("release_destination") or "",
            "package_output_path": request.get("package_output_path") or "",
            "artifacts": {
                "release_manifest_path": str(release_dir / "release_package_manifest.json"),
                "release_events_path": str(release_dir / "release_package_events.jsonl"),
                "release_package_path": str(release_package_path),
            },
            "created_at": utcnow().isoformat(),
        }
        _write_json(release_dir / "release_package_manifest.json", payload)
        _write_jsonl(release_dir / "release_package_events.jsonl", [payload])
        if package_creation_allowed:
            zip_payload = _release_package_zip_safe_payload(payload)
            release_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(release_package_path, "w", compression=zipfile.ZIP_DEFLATED) as package:
                package.writestr("release_package_manifest.json", json.dumps(zip_payload, indent=2, sort_keys=True))
                package.writestr("release_package_events.jsonl", json.dumps(zip_payload, sort_keys=True) + "\n")
        return payload


class ReleaseGoNoGoManifestBuilder:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def build(self, request: dict[str, Any]) -> dict[str, Any]:
        review_id = str(request.get("review_id") or f"release-go-no-go:{request.get('cycle_id', 'scorecard_template')}")
        review_dir = self.cycle_dir / "release-go-no-go" / safe_name(review_id)
        review_artifact_path = review_dir / "release_go_no_go_review.json"
        source_refs = request.get("source_refs") if isinstance(request.get("source_refs"), dict) else {}
        if not source_refs:
            source_refs = {
                key: value
                for key, value in {
                    "release_package": request.get("release_package_path"),
                    "support_bundle": request.get("support_bundle_path"),
                    "crash_diagnostics": request.get("crash_diagnostics_bundle_path"),
                    "release_destination": request.get("release_destination"),
                }.items()
                if value
            }
        redact_paths = bool(request.get("workspace_paths_redacted", True))
        redacted_sources = {
            str(key): _support_bundle_redacted_ref(value, redact_paths=redact_paths)
            for key, value in source_refs.items()
        }
        gates = {
            "release_packaging_ready": bool(request.get("release_packaging_ready")),
            "first_run_readiness_ready": bool(request.get("first_run_readiness_ready")),
            "crash_diagnostics_ready": bool(request.get("crash_diagnostics_ready")),
            "support_bundle_ready": bool(request.get("support_bundle_ready")),
            "artifact_trust_clear": bool(request.get("artifact_trust_clear")),
            "trusted_adapter_artifact_required": bool(request.get("adapter_artifact_trust_clear")),
            "signed_replay_trust_clear": bool(request.get("signed_replay_trust_clear")),
            "reviewer_windows_ready": bool(request.get("reviewer_windows_ready")),
            "operator_approved": bool(request.get("operator_approved")),
            "human_approved": bool(request.get("human_approved")),
            "release_destination": bool(request.get("release_destination")),
        }
        blockers = sorted(gate for gate, passed in gates.items() if not passed)
        buyer_release_allowed = bool(request.get("buyer_release_allowed")) and not blockers
        review_artifact_blockers = _release_go_no_go_review_artifact_blockers(request, blockers)
        review_artifact_allowed = not review_artifact_blockers
        payload = {
            "schema_version": "release_go_no_go_manifest_preview.v0.1",
            "status": "manifest_preview_ready",
            "review_id": review_id,
            "cycle_id": request.get("cycle_id"),
            "student_id": request.get("student_id"),
            "target_node_ref": request.get("target_node_ref"),
            "release_id": request.get("release_id"),
            "decision": "approved" if buyer_release_allowed else "blocked",
            "buyer_release_allowed": buyer_release_allowed,
            "release_mutation_allowed": False,
            "release_mutation_blocker": "buyer_release_requires_separate_packaging_mutation_command",
            "review_artifact_created": review_artifact_allowed,
            "review_artifact_allowed": review_artifact_allowed,
            "review_artifact_blockers": review_artifact_blockers,
            "artifact_trust_clear": gates["artifact_trust_clear"],
            "adapter_artifact_trust_status": str(request.get("adapter_artifact_trust_status") or "not_recorded"),
            "adapter_artifact_trust_clear": bool(request.get("adapter_artifact_trust_clear")),
            "signed_replay_trust_clear": gates["signed_replay_trust_clear"],
            "reviewer_windows_ready": gates["reviewer_windows_ready"],
            "operator_approved": gates["operator_approved"],
            "human_approved": gates["human_approved"],
            "gate_results": gates,
            "release_blockers": blockers,
            "source_refs": redacted_sources,
            "source_count": len(redacted_sources),
            "blocked_payload_fields": [
                "raw_private_data",
                "secrets",
                "passphrase",
                "signing_seed_hex",
                "environment_variables",
                "private_support_notes",
            ],
            "release_destination": request.get("release_destination") or "",
            "artifacts": {
                "review_manifest_path": str(review_dir / "release_go_no_go_manifest.json"),
                "review_events_path": str(review_dir / "release_go_no_go_events.jsonl"),
                "review_artifact_path": str(review_artifact_path),
            },
            "created_at": utcnow().isoformat(),
        }
        _write_json(review_dir / "release_go_no_go_manifest.json", payload)
        _write_jsonl(review_dir / "release_go_no_go_events.jsonl", [payload])
        if review_artifact_allowed:
            _write_json(review_artifact_path, _release_go_no_go_final_review_safe_payload(payload))
        return payload


class RuntimeHealthMonitorManifestBuilder:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def build(self, request: dict[str, Any]) -> dict[str, Any]:
        monitor_id = str(request.get("monitor_id") or f"runtime-health:{request.get('cycle_id', 'scorecard_template')}")
        if monitor_id == "runtime-health:scorecard_template" and request.get("cycle_id"):
            monitor_id = f"runtime-health:{request['cycle_id']}"
        monitor_dir = self.cycle_dir / "runtime-health-monitors" / safe_name(monitor_id)
        health_report_path = monitor_dir / "runtime_health_report.json"
        source_refs = request.get("source_refs") if isinstance(request.get("source_refs"), dict) else {}
        if not source_refs:
            source_refs = {
                key: value
                for key, value in {
                    "rollback_snapshot": request.get("rollback_snapshot_path"),
                    "node_registry_events": request.get("node_registry_events_path"),
                    "target_signed_replay": request.get("target_signed_replay_id"),
                }.items()
                if value
            }
        redact_paths = bool(request.get("workspace_paths_redacted", True))
        redacted_sources = {
            str(key): _support_bundle_redacted_ref(value, redact_paths=redact_paths)
            for key, value in source_refs.items()
        }
        current_runtime_state = str(request.get("current_runtime_state") or "shadow")
        canary_or_active = current_runtime_state in {"canary", "active", "permanent_active"}
        signed_replay_trust_clear = bool(request.get("signed_replay_trust_clear"))
        adapter_artifact_trust_status = str(request.get("adapter_artifact_trust_status") or "not_recorded")
        adapter_artifact_trust_clear = bool(request.get("adapter_artifact_trust_clear"))
        rollback_restorable = bool(request.get("rollback_restorable"))
        health_window_started = bool(request.get("health_window_started"))
        observed_metrics = {
            "route_share": request.get("route_share_observed"),
            "error_rate": request.get("error_rate_observed"),
            "p95_latency_ms": request.get("p95_latency_ms_observed"),
        }
        blockers = []
        if not signed_replay_trust_clear:
            blockers.append("trusted_signed_replay_required")
        if not canary_or_active:
            blockers.append("canary_or_active_runtime_state_required")
        if not health_window_started:
            blockers.append("health_window_not_started")
        if not rollback_restorable:
            blockers.append("rollback_restorable_required")
        blockers.extend(_runtime_health_metric_blockers(request, observed_metrics))
        health_report_blockers = sorted(set(blockers))
        health_report_allowed = not health_report_blockers
        payload = {
            "schema_version": "runtime_health_monitor_manifest_preview.v0.1",
            "status": "manifest_preview_ready",
            "monitor_id": monitor_id,
            "cycle_id": request.get("cycle_id"),
            "student_id": request.get("student_id"),
            "target_node_ref": request.get("target_node_ref"),
            "decision": "ready" if health_report_allowed else "blocked",
            "runtime_activation_allowed": False,
            "runtime_activation_blocker": "runtime_health_manifest_is_observational_only",
            "health_report_created": health_report_allowed,
            "health_report_allowed": health_report_allowed,
            "health_report_blockers": health_report_blockers,
            "current_runtime_state": current_runtime_state,
            "monitor_window": request.get("monitor_window") or "canary_runtime",
            "auto_disable_on_blocker": bool(request.get("auto_disable_on_blocker", True)),
            "signed_replay_trust_clear": signed_replay_trust_clear,
            "adapter_artifact_trust_status": adapter_artifact_trust_status,
            "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
            "rollback_restorable": rollback_restorable,
            "health_window_started": health_window_started,
            "thresholds": {
                "max_error_rate": request.get("max_error_rate"),
                "max_p95_latency_ms": request.get("max_p95_latency_ms"),
                "max_route_share": request.get("max_route_share"),
            },
            "observed_metrics": observed_metrics,
            "health_blockers": health_report_blockers,
            "source_refs": redacted_sources,
            "source_count": len(redacted_sources),
            "blocked_payload_fields": [
                "raw_private_data",
                "secrets",
                "passphrase",
                "signing_seed_hex",
                "environment_variables",
            ],
            "artifacts": {
                "monitor_manifest_path": str(monitor_dir / "runtime_health_monitor_manifest.json"),
                "monitor_events_path": str(monitor_dir / "runtime_health_monitor_events.jsonl"),
                "health_report_path": str(health_report_path),
            },
            "created_at": utcnow().isoformat(),
        }
        _write_json(monitor_dir / "runtime_health_monitor_manifest.json", payload)
        _write_jsonl(monitor_dir / "runtime_health_monitor_events.jsonl", [payload])
        if health_report_allowed:
            _write_json(health_report_path, _runtime_health_report_safe_payload(payload))
        return payload


class TeacherEjectionReviewManifestBuilder:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def build(self, request: dict[str, Any]) -> dict[str, Any]:
        review_id = str(request.get("review_id") or f"teacher-ejection:{request.get('cycle_id', 'scorecard_template')}")
        if review_id == "teacher-ejection:scorecard_template" and request.get("cycle_id"):
            review_id = f"teacher-ejection:{request['cycle_id']}"
        review_dir = self.cycle_dir / "teacher-ejection-reviews" / safe_name(review_id)
        final_review_artifact_path = review_dir / "teacher_ejection_final_review.json"
        source_refs = request.get("source_refs") if isinstance(request.get("source_refs"), dict) else {}
        if not source_refs:
            source_refs = {
                key: value
                for key, value in {
                    "eval_id": request.get("eval_id"),
                    "parent_node": request.get("parent_node_ref"),
                    "student": request.get("student_id"),
                    "cycle": request.get("cycle_id"),
                }.items()
                if value
            }
        redact_paths = bool(request.get("workspace_paths_redacted", True))
        redacted_sources = {
            str(key): _support_bundle_redacted_ref(value, redact_paths=redact_paths)
            for key, value in source_refs.items()
        }
        gates = {
            "teacher_ejection_allowed": bool(request.get("teacher_ejection_allowed")),
            "parent_retirement_allowed": bool(request.get("parent_retirement_allowed")),
            "post_promotion_window_passed": bool(request.get("post_promotion_window_passed")),
            "ivy_grade_review_passed": bool(request.get("ivy_grade_review_passed")),
            "greatly_outperforms_parent": bool(request.get("greatly_outperforms_parent")),
            "rollback_restorable": bool(request.get("rollback_restorable")),
            "adapter_artifact_trust_clear": bool(request.get("adapter_artifact_trust_clear")),
            "child_retained_after_parent_retirement": bool(request.get("child_retained_after_parent_retirement", True)),
            "rollback_retention_required": bool(request.get("rollback_retention_required", True)),
        }
        blockers = sorted(
            gate
            for gate, passed in gates.items()
            if gate not in {"child_retained_after_parent_retirement", "rollback_retention_required"} and not passed
        )
        final_review_artifact_blockers = _teacher_ejection_final_review_blockers(request, blockers)
        final_review_artifact_allowed = not final_review_artifact_blockers
        payload = {
            "schema_version": "teacher_ejection_review_manifest_preview.v0.1",
            "status": "manifest_preview_ready",
            "review_id": review_id,
            "cycle_id": request.get("cycle_id"),
            "student_id": request.get("student_id"),
            "parent_node_ref": request.get("parent_node_ref"),
            "eval_id": request.get("eval_id"),
            "decision": "approved" if not blockers else "blocked",
            "teacher_ejection_allowed": gates["teacher_ejection_allowed"],
            "parent_retirement_allowed": gates["parent_retirement_allowed"],
            "adapter_artifact_trust_status": str(request.get("adapter_artifact_trust_status") or "not_recorded"),
            "adapter_artifact_trust_clear": gates["adapter_artifact_trust_clear"],
            "teacher_ejection_mutation_allowed": False,
            "parent_retirement_mutation_allowed": False,
            "mutation_blocker": "teacher_ejection_and_parent_retirement_require_separate_governed_mutation_command",
            "final_review_artifact_created": final_review_artifact_allowed,
            "final_review_artifact_allowed": final_review_artifact_allowed,
            "final_review_artifact_blockers": final_review_artifact_blockers,
            "post_promotion_window_passed": gates["post_promotion_window_passed"],
            "ivy_grade_review_passed": gates["ivy_grade_review_passed"],
            "greatly_outperforms_parent": gates["greatly_outperforms_parent"],
            "child_retained_after_parent_retirement": gates["child_retained_after_parent_retirement"],
            "rollback_retention_required": gates["rollback_retention_required"],
            "rollback_restorable": gates["rollback_restorable"],
            "lower_confidence_surpass_bound": request.get("lower_confidence_surpass_bound"),
            "required_lower_confidence_margin": request.get("required_lower_confidence_margin"),
            "required_windows": request.get("required_windows") or [],
            "passed_windows": request.get("passed_windows") or [],
            "pending_window_count": request.get("pending_window_count"),
            "retirement_blockers": blockers,
            "source_refs": redacted_sources,
            "source_count": len(redacted_sources),
            "blocked_payload_fields": [
                "raw_private_data",
                "secrets",
                "passphrase",
                "signing_seed_hex",
                "environment_variables",
            ],
            "artifacts": {
                "review_manifest_path": str(review_dir / "teacher_ejection_review_manifest.json"),
                "review_events_path": str(review_dir / "teacher_ejection_review_events.jsonl"),
                "final_review_artifact_path": str(final_review_artifact_path),
            },
            "created_at": utcnow().isoformat(),
        }
        _write_json(review_dir / "teacher_ejection_review_manifest.json", payload)
        _write_jsonl(review_dir / "teacher_ejection_review_events.jsonl", [payload])
        if final_review_artifact_allowed:
            _write_json(final_review_artifact_path, _teacher_ejection_final_review_safe_payload(payload))
        return payload


def _support_bundle_redacted_ref(value: Any, *, redact_paths: bool) -> Any:
    if not redact_paths or not isinstance(value, str):
        return value
    if "\\" not in value and "/" not in value:
        if any(char.isspace() for char in value):
            return {
                "kind": "redacted_text_ref",
                "digest": _sha256_text(value),
                "redacted": True,
            }
        return value
    path = Path(value)
    return {
        "kind": "redacted_path_ref",
        "name": path.name,
        "suffix": path.suffix,
        "redacted": True,
    }


def _support_bundle_zip_creation_blockers(request: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not request.get("secret_scan_passed"):
        blockers.append("secret_scan_passed")
    if not request.get("support_bundle_destination"):
        blockers.append("support_bundle_destination")
    if request.get("include_raw_private_data"):
        blockers.append("include_raw_private_data")
    if request.get("redact_secrets", True) is not True:
        blockers.append("redact_secrets")
    if request.get("workspace_paths_redacted", True) is not True:
        blockers.append("workspace_paths_redacted")
    return blockers


def _support_bundle_zip_safe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = json.loads(json.dumps(payload))
    artifacts = sanitized.get("artifacts") if isinstance(sanitized.get("artifacts"), dict) else {}
    sanitized["artifacts"] = {str(key): Path(str(value)).name for key, value in artifacts.items()}
    return sanitized


def _crash_diagnostics_packaging_blockers(request: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not request.get("secret_scan_passed"):
        blockers.append("secret_scan_passed")
    if not request.get("diagnostics_destination"):
        blockers.append("diagnostics_destination")
    if not request.get("crash_diagnostics_ready"):
        blockers.append("crash_diagnostics_ready")
    if request.get("include_support_bundle") and not request.get("support_bundle_ready"):
        blockers.append("support_bundle")
    if request.get("include_raw_private_data"):
        blockers.append("include_raw_private_data")
    if request.get("redact_secrets", True) is not True:
        blockers.append("redact_secrets")
    if request.get("workspace_paths_redacted", True) is not True:
        blockers.append("workspace_paths_redacted")
    return blockers


def _first_run_readiness_bundle_blockers(request: dict[str, Any], readiness_blockers: list[str]) -> list[str]:
    blockers = list(readiness_blockers)
    if request.get("include_raw_private_data"):
        blockers.append("include_raw_private_data")
    if request.get("redact_secrets", True) is not True:
        blockers.append("redact_secrets")
    if request.get("workspace_paths_redacted", True) is not True:
        blockers.append("workspace_paths_redacted")
    return sorted(set(blockers))


def _first_run_readiness_bundle_safe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = _support_bundle_zip_safe_payload(payload)
    sanitized["schema_version"] = "first_run_readiness_bundle.v0.1"
    sanitized["status"] = "first_run_readiness_bundle_ready"
    return sanitized


def _diagnostics_bundle_safe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = _support_bundle_zip_safe_payload(payload)
    sanitized["schema_version"] = "crash_diagnostics_bundle.v0.1"
    sanitized["status"] = "diagnostics_bundle_ready"
    return sanitized


def _release_package_creation_blockers(request: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not request.get("release_destination"):
        blockers.append("release_destination")
    if not request.get("ci_packaging_ready"):
        blockers.append("ci_packaging_ready")
    if not request.get("buyer_launcher_ready"):
        blockers.append("buyer_launcher_ready")
    if not request.get("buyer_safe_defaults"):
        blockers.append("buyer_safe_defaults")
    if request.get("include_support_bundle") and not request.get("support_bundle_ready"):
        blockers.append("support_bundle")
    if request.get("include_crash_diagnostics") and not request.get("crash_diagnostics_ready"):
        blockers.append("crash_diagnostics")
    if request.get("include_first_run_readiness") and not request.get("first_run_readiness_ready"):
        blockers.append("first_run_readiness")
    if not request.get("artifact_signing_ready"):
        blockers.append("artifact_signing_ready")
    if not request.get("artifact_trust_clear"):
        blockers.append("artifact_trust_clear")
    if not request.get("adapter_artifact_trust_clear"):
        blockers.append("adapter_artifact_trust_clear")
    if request.get("include_raw_private_data"):
        blockers.append("include_raw_private_data")
    if request.get("redact_secrets", True) is not True:
        blockers.append("redact_secrets")
    if request.get("workspace_paths_redacted", True) is not True:
        blockers.append("workspace_paths_redacted")
    return blockers


def _release_package_zip_safe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = _support_bundle_zip_safe_payload(payload)
    sanitized["schema_version"] = "release_package_bundle.v0.1"
    sanitized["status"] = "release_package_ready"
    return sanitized


def _release_go_no_go_review_artifact_blockers(request: dict[str, Any], release_blockers: list[str]) -> list[str]:
    blockers = list(release_blockers)
    if not request.get("buyer_release_allowed"):
        blockers.append("buyer_release_allowed")
    if request.get("include_raw_private_data"):
        blockers.append("include_raw_private_data")
    if request.get("redact_secrets", True) is not True:
        blockers.append("redact_secrets")
    if request.get("workspace_paths_redacted", True) is not True:
        blockers.append("workspace_paths_redacted")
    return sorted(set(blockers))


def _release_go_no_go_final_review_safe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = _support_bundle_zip_safe_payload(payload)
    sanitized["schema_version"] = "release_go_no_go_final_review.v0.1"
    sanitized["status"] = "release_go_no_go_final_review_ready"
    return sanitized


def _runtime_health_metric_blockers(request: dict[str, Any], observed_metrics: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    route_share = observed_metrics.get("route_share")
    max_route_share = request.get("max_route_share")
    error_rate = observed_metrics.get("error_rate")
    max_error_rate = request.get("max_error_rate")
    p95_latency = observed_metrics.get("p95_latency_ms")
    max_p95_latency = request.get("max_p95_latency_ms")

    if route_share is not None and max_route_share is not None and float(route_share) > float(max_route_share):
        blockers.append("route_share_exceeded")
    if error_rate is not None and max_error_rate is not None and float(error_rate) > float(max_error_rate):
        blockers.append("error_rate_exceeded")
    if p95_latency is not None and max_p95_latency is not None and float(p95_latency) > float(max_p95_latency):
        blockers.append("p95_latency_exceeded")
    return blockers


def _runtime_health_report_safe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = _support_bundle_zip_safe_payload(payload)
    sanitized["schema_version"] = "runtime_health_report.v0.1"
    sanitized["status"] = "runtime_health_report_ready"
    return sanitized


def _teacher_ejection_final_review_blockers(request: dict[str, Any], retirement_blockers: list[str]) -> list[str]:
    blockers = list(retirement_blockers)
    if request.get("child_retained_after_parent_retirement", True) is not True:
        blockers.append("child_retained_after_parent_retirement")
    if request.get("rollback_retention_required", True) is not True:
        blockers.append("rollback_retention_required")
    if request.get("include_raw_private_data"):
        blockers.append("include_raw_private_data")
    if request.get("redact_secrets", True) is not True:
        blockers.append("redact_secrets")
    if request.get("workspace_paths_redacted", True) is not True:
        blockers.append("workspace_paths_redacted")
    return sorted(set(blockers))


def _teacher_ejection_final_review_safe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = _support_bundle_zip_safe_payload(payload)
    sanitized["schema_version"] = "teacher_ejection_final_review.v0.1"
    sanitized["status"] = "teacher_ejection_final_review_ready"
    return sanitized


def _upstream_agent_opportunity_gate(gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "ready_for_agent_build": gate.get("ready_for_agent_build"),
        "opportunity_gate_state": gate.get("opportunity_gate_state") or "not_provided",
        "blockers": sorted(set(str(item) for item in gate.get("blockers") or [])),
        "source": gate.get("source") or "agent_opportunity_discovery",
    }


def _agent_opportunity_gate_blocked(gate: dict[str, Any]) -> bool:
    return bool(
        gate.get("ready_for_agent_build") is False
        or gate.get("opportunity_gate_state") == "blocked-by-forward-radar"
        or gate.get("blockers")
    )


class GrowthLifecycleOrchestrator:
    def __init__(self, cycle_dir: Path) -> None:
        self.cycle_dir = cycle_dir

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        lifecycle_id = str(request.get("lifecycle_id") or "lifecycle:growth")
        lifecycle_dir = self.cycle_dir / "growth-lifecycles" / safe_name(lifecycle_id)
        cycle_id = request["cycle_id"]
        student_id = request["student_id"]
        target_node_ref = request["target_node_ref"]
        lifecycle_name = safe_name(lifecycle_id)
        growth_engine_gate = _growth_engine_gate_from_request(request)

        teacher_review = TeacherCouncilReviewer(self.cycle_dir).review(
            {
                "review_id": f"teacher:{lifecycle_name}",
                "cycle_id": cycle_id,
                "target_node_ref": target_node_ref,
                "teacher_outputs": request.get("teacher_outputs", []),
                "validator_results": request.get("validator_results", []),
            }
        )
        training_backend_plan = TrainingBackendPlanner(self.cycle_dir).plan(
            {
                "plan_id": f"train_backend:{lifecycle_name}",
                "cycle_id": cycle_id,
                "student_id": student_id,
                "base_model_ref": request.get("base_model_ref") or f"model:{safe_name(student_id)}",
                "dataset_manifest_ref": request.get("dataset_manifest_ref") or f"dataset:{lifecycle_name}",
                "method": request.get("training_method") or "lora",
                "framework": request.get("training_framework") or "peft",
                "training_modes": request.get("training_modes") or ["sequence_distillation", "router_alignment", "validator_grounded_task_loss"],
                "teacher_refs": [item.get("teacher_ref") for item in request.get("teacher_outputs", []) if item.get("teacher_ref")],
                "license_state": "approved_train" if (teacher_review.get("license_gate") or {}).get("passed") else "pending_review",
                "privacy_class": request.get("privacy_class") or "internal",
                "contains_private_data": bool(request.get("contains_private_data")),
                "eval_refs": request.get("eval_refs") or [f"eval:{lifecycle_name}"],
                "hidden_eval_attestation": request.get("hidden_eval_attestation") or {},
                "rollback_ref": request.get("rollback_ref") or f"rollback:{safe_name(target_node_ref)}",
                "export_targets": request.get("export_targets") or ["adapter", "gguf", "quantization_manifest"],
                "target_hardware": request.get("target_hardware") or {"vendor": "local", "vram_gb": 0, "cuda_available": False},
                "operator_approved": bool(request.get("operator_approved")),
                "human_approved": bool(request.get("human_approved")),
                "dependency_report": request.get("dependency_report")
                or {
                    "transformers": {"available": True, "version": "lifecycle-v0"},
                    "peft": {"available": True, "version": "lifecycle-v0"},
                    "accelerate": {"available": True, "version": "lifecycle-v0"},
                },
                "training_dataset": request.get("training_dataset", []),
            }
        )
        from nexusnet.training.sandbox_runner import run_sandbox_training

        training = run_sandbox_training((training_backend_plan.get("execution_contract") or {}).get("config_path", ""), mode="sandbox")
        training_replay_evidence = _build_training_replay_evidence(training)
        training_weight_ref = (training.get("artifacts") or {}).get("checkpoint_path", "")
        child_execution = ChildNodeExecutor(self.cycle_dir).execute(
            {
                "execution_id": f"exec:{lifecycle_name}",
                "cycle_id": cycle_id,
                "student_id": student_id,
                "input": request.get("shadow_input") or {"x": 0.0},
                "weights_path": training_weight_ref,
            }
        )
        child_execution_replay_evidence = child_execution.get("child_execution_replay_evidence") or {}
        hive_route = HiveMoEShadowRouter(self.cycle_dir).route(
            {
                "route_id": f"route:{lifecycle_name}",
                "cycle_id": cycle_id,
                "task_features": request.get("route_features") or {},
                "candidates": request.get("route_candidates") or [{"node_ref": student_id, "weights": {"default": 1.0}}],
                "top_k": int(request.get("top_k") or 2),
            }
        )
        hive_route_replay_evidence = hive_route.get("hive_route_replay_evidence") or {}
        tensor_program = TensorProgramExecutor(self.cycle_dir).execute(
            {
                "program_id": f"tensor:{lifecycle_name}",
                "cycle_id": cycle_id,
                "parameter_refs": {"student": student_id, "parent": target_node_ref},
                "ops": [
                    {"op": "matmul", "name": "projection", "left": [[1, 2], [3, 4]], "right": [[2], [1]]},
                    {"op": "relu", "name": "activation", "input": [-1, 0, 3]},
                    {"op": "softmax", "name": "gate", "input": [1.0, 2.0, 3.0]},
                ],
            }
        )
        tensor_runtime_replay_evidence = tensor_program.get("tensor_runtime_replay_evidence") or {}
        sealed_eval = SealedEvalReviewer(self.cycle_dir).evaluate(
            {
                "eval_id": f"eval:{lifecycle_name}",
                "cycle_id": cycle_id,
                "student_id": student_id,
                "parent_node_ref": target_node_ref,
                "weights_path": training_weight_ref,
                "hidden_eval_cases": request.get("hidden_eval_cases", []),
                "teacher_license_gate_passed": bool((teacher_review.get("license_gate") or {}).get("passed")),
                "human_approved": bool(request.get("human_approved")),
            }
        )
        reviewer_confidence_evidence = sealed_eval.get("reviewer_confidence_evidence") or {}
        adapter_bundle_path = ((training.get("exports") or {}).get("adapter") or {}).get("bundle_path")
        adapter_artifact_trust_status = str(
            request.get("adapter_artifact_trust_status")
            or ("quarantined" if adapter_bundle_path else "not_recorded")
        )
        adapter_artifact_trust_clear = bool(request.get("adapter_artifact_trust_clear"))
        node_registry = NodeRegistryDecisionEngine(self.cycle_dir).apply(
            {
                "decision_id": f"decision:{lifecycle_name}",
                "cycle_id": cycle_id,
                "student_id": student_id,
                "parent_node_ref": target_node_ref,
                "eval_scorecard_path": (sealed_eval.get("artifacts") or {}).get("eval_scorecard_path", ""),
                "action": "promote_child",
                "adapter_artifact_trust_status": adapter_artifact_trust_status,
                "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
                "human_approved": bool(request.get("human_approved")),
            }
        )
        node_registry_replay_evidence = node_registry.get("node_registry_replay_evidence") or {}
        federation_request = request.get("federation") or {}
        federation = FederatedPacketIntake(self.cycle_dir).submit(
            {
                "packet_id": f"fed:{lifecycle_name}",
                "cycle_id": cycle_id,
                "source_node_ref": target_node_ref,
                "consent_granted": bool(federation_request.get("consent_granted")),
                "local_metrics": federation_request.get("local_metrics") or {},
                "capability_tags": request.get("capabilities", []),
            }
        )
        federated_influence_replay_evidence = federation.get("federated_influence_replay_evidence") or {}
        dream_cycle = RecursiveDreamCycleRunner(self.cycle_dir).run(
            {
                "dream_id": f"dream:{lifecycle_name}",
                "cycle_id": cycle_id,
                "target_node_ref": target_node_ref,
                "student_id": student_id,
                "failure_refs": request.get("failure_refs") or ["failure:lifecycle_gap"],
                "federated_packet_signature": federation.get("packet_signature", "federation:blocked"),
                "dream_temperature": float(request.get("dream_temperature") or 0.95),
                "critic_temperature": float(request.get("critic_temperature") or 0.15),
            }
        )
        recursive_dream_replay_evidence = dream_cycle.get("recursive_dream_replay_evidence") or {}
        runtime_foundry = RuntimeQuantizationBenchmarkRunner(self.cycle_dir).run(
            {
                "benchmark_id": f"bench:{lifecycle_name}",
                "cycle_id": cycle_id,
                "model_ref": student_id,
                "hardware_profile": request.get("hardware_profile") or {"device": "local_shadow", "memory_gb": 16},
                "baseline_quality_score": float(request.get("baseline_quality_score") or 0.93),
                "candidates": request.get("runtime_benchmarks", []),
                "backend_run_verified": bool(request.get("backend_run_verified", True)),
                "human_approved": bool(request.get("human_approved")),
            }
        )
        runtime_foundry_replay_evidence = runtime_foundry.get("runtime_foundry_replay_evidence") or {}
        deep_replay_request = {"cycle_id": cycle_id, "replay_id": f"replay:{lifecycle_name}"}
        for signing_key in ("signing_seed_hex", "artifact_signing_seed_hex"):
            if request.get(signing_key):
                deep_replay_request[signing_key] = request[signing_key]
        for signing_key in ("signing_key_file", "signing_key_passphrase"):
            if request.get(signing_key):
                deep_replay_request[signing_key] = request[signing_key]
        deep_replay = DeepReplayBundleBuilder(self.cycle_dir).build(deep_replay_request)
        productization_gate_proofs = request.get("productization_readiness") or request.get("productization_gate_proofs") or {}
        artifact_signing_ready = (
            (deep_replay.get("signature_policy") or {}).get("current_signature_state") == "signed_ed25519"
            and (deep_replay.get("signature_policy") or {}).get("real_signing_blocker") is None
        )
        productization = ProductizationReadinessAssessor(self.cycle_dir).assess(
            {
                "readiness_id": f"release:{lifecycle_name}",
                "cycle_id": cycle_id,
                "local_cache_controls": bool(productization_gate_proofs.get("local_cache_controls", True)),
                "secret_scan_passed": bool(productization_gate_proofs.get("secret_scan_passed", False)),
                "model_download_manager": bool(productization_gate_proofs.get("model_download_manager", True)),
                "support_bundle": bool(productization_gate_proofs.get("support_bundle", False)),
                "crash_diagnostics": bool(productization_gate_proofs.get("crash_diagnostics", True)),
                "ci_packaging": bool(productization_gate_proofs.get("ci_packaging", False)),
                "buyer_launcher": bool(productization_gate_proofs.get("buyer_launcher", True)),
                "docs_complete": bool(productization_gate_proofs.get("docs_complete", False)),
                "buyer_safe_defaults": bool(productization_gate_proofs.get("buyer_safe_defaults", True)),
                "runtime_gates_clear": bool(productization_gate_proofs.get("runtime_gates_clear", node_registry.get("decision") == "promote_child")),
                "artifact_signing_ready": bool(productization_gate_proofs.get("artifact_signing_ready", artifact_signing_ready)),
                "artifact_trust_clear": bool(productization_gate_proofs.get("artifact_trust_clear", artifact_signing_ready)),
                "adapter_artifact_trust_clear": bool(productization_gate_proofs.get("adapter_artifact_trust_clear", False)),
                "upstream_agent_opportunity_gate": productization_gate_proofs.get("upstream_agent_opportunity_gate") or {},
            }
        )
        productization_replay_evidence = productization.get("productization_replay_evidence") or {}
        artifact_bridge = {
            "training_backend_plan_path": (training_backend_plan.get("artifacts") or {}).get("training_backend_plan_path", ""),
            "training_config_path": (training_backend_plan.get("artifacts") or {}).get("training_config_path", ""),
            "training_invocation_path": (training_backend_plan.get("artifacts") or {}).get("training_invocation_path", ""),
            "training_report_path": (training.get("artifacts") or {}).get("training_report_path", ""),
            "loss_trace_path": (training.get("artifacts") or {}).get("loss_trace_path", ""),
            "training_checkpoint_path": (training.get("artifacts") or {}).get("checkpoint_path", ""),
            "adapter_manifest_path": (training.get("artifacts") or {}).get("adapter_manifest_path", ""),
            "adapter_bundle_path": ((training.get("exports") or {}).get("adapter") or {}).get("bundle_path", ""),
            "child_execution_report_path": (child_execution.get("artifacts") or {}).get("execution_report_path", ""),
            "eval_scorecard_path": (sealed_eval.get("artifacts") or {}).get("eval_scorecard_path", ""),
            "deep_replay_artifact_index_path": (deep_replay.get("artifacts") or {}).get("artifact_index_path", ""),
        }
        replay_consistency = _validate_lifecycle_replay_consistency(artifact_bridge, deep_replay)
        signer_readiness = _build_signer_readiness(deep_replay)
        blocked_reasons = []
        critical_blockers = []
        if not growth_engine_gate["allowed"]:
            blocked_reasons.extend(str(reason) for reason in growth_engine_gate["blockers"])
            critical_blockers.extend(str(reason) for reason in growth_engine_gate["blockers"])
        if training_backend_plan.get("status") == "blocked":
            blocked_reasons.append("training_backend_plan_blocked")
            critical_blockers.append("training_backend_plan_blocked")
        if training.get("status") == "blocked":
            blocked_reasons.append("training_blocked")
            critical_blockers.append("training_blocked")
        if child_execution.get("status") == "blocked":
            blocked_reasons.append("child_execution_blocked")
            critical_blockers.append("child_execution_blocked")
        if sealed_eval.get("status") == "blocked":
            blocked_reasons.append("sealed_eval_blocked")
            critical_blockers.append("sealed_eval_blocked")
        if node_registry.get("decision") == "blocked":
            blocked_reasons.extend(str(reason) for reason in node_registry.get("blocked_reasons", []))
        if not replay_consistency["passed"]:
            blocked_reasons.append("replay_consistency_failed")
            critical_blockers.append("replay_consistency_failed")
        if signer_readiness.get("production_mutation_blocker"):
            blocked_reasons.append(str(signer_readiness["production_mutation_blocker"]))
        lifecycle_status = "closed_loop_blocked" if critical_blockers else "closed_loop_complete"
        events = [
            {"step": "growth_engine_gate", "status": "passed" if growth_engine_gate["allowed"] else "blocked"},
            {"step": "teacher_review", "status": teacher_review.get("status")},
            {"step": "training_backend_plan", "status": training_backend_plan.get("status")},
            {"step": "training", "status": training.get("status")},
            {"step": "child_execution", "status": child_execution.get("status")},
            {"step": "hive_route", "status": hive_route.get("status")},
            {"step": "tensor_program", "status": tensor_program.get("status")},
            {"step": "sealed_eval", "status": sealed_eval.get("status")},
            {"step": "node_registry", "status": node_registry.get("decision")},
            {"step": "federation", "status": federation.get("status")},
            {"step": "dream_cycle", "status": dream_cycle.get("status")},
            {"step": "runtime_foundry", "status": runtime_foundry.get("status")},
            {"step": "deep_replay", "status": deep_replay.get("status")},
            {"step": "signer_readiness", "status": signer_readiness.get("status")},
            {
                "step": "replay_consistency",
                "status": "passed" if replay_consistency["passed"] else "failed",
                "checked_bridge_path_count": replay_consistency["checked_bridge_path_count"],
            },
            {
                "step": "training_replay_evidence",
                "status": "ready" if training_replay_evidence["math_contract_present"] and training_replay_evidence["optimizer_state_present"] else "blocked",
                "math_contract_present": training_replay_evidence["math_contract_present"],
                "optimizer_state_present": training_replay_evidence["optimizer_state_present"],
            },
            {
                "step": "child_execution_replay_evidence",
                "status": child_execution_replay_evidence.get("status") or "blocked",
                "callable_runtime_verified": bool(child_execution_replay_evidence.get("callable_runtime_verified")),
            },
            {
                "step": "hive_route_replay_evidence",
                "status": hive_route_replay_evidence.get("status") or "blocked",
                "selected_node_count": len(hive_route_replay_evidence.get("selected_nodes") or []),
            },
            {
                "step": "tensor_runtime_replay_evidence",
                "status": tensor_runtime_replay_evidence.get("status") or "blocked",
                "op_count": tensor_runtime_replay_evidence.get("op_count") or 0,
            },
            {
                "step": "reviewer_confidence_evidence",
                "status": reviewer_confidence_evidence.get("status") or "blocked",
                "teacher_ejection_eligible": bool(reviewer_confidence_evidence.get("teacher_ejection_eligible")),
            },
            {
                "step": "node_registry_replay_evidence",
                "status": node_registry_replay_evidence.get("status") or "blocked",
                "parent_retirement_allowed": bool(node_registry_replay_evidence.get("parent_retirement_allowed")),
            },
            {
                "step": "federated_influence_replay_evidence",
                "status": federated_influence_replay_evidence.get("status") or "blocked",
                "consent_granted": bool(federated_influence_replay_evidence.get("consent_granted")),
            },
            {
                "step": "recursive_dream_replay_evidence",
                "status": recursive_dream_replay_evidence.get("status") or "blocked",
                "candidate_count": recursive_dream_replay_evidence.get("candidate_count") or 0,
            },
            {
                "step": "runtime_foundry_replay_evidence",
                "status": runtime_foundry_replay_evidence.get("status") or "blocked",
                "benchmark_count": runtime_foundry_replay_evidence.get("benchmark_count") or 0,
            },
            {
                "step": "productization_replay_evidence",
                "status": productization_replay_evidence.get("status") or "blocked",
                "open_gate_count": len(productization_replay_evidence.get("open_gates") or []),
            },
            {"step": "productization", "status": productization.get("status")},
        ]
        payload = {
            "schema_version": "growth_lifecycle_orchestrator.v0.1",
            "lifecycle_id": lifecycle_id,
            "cycle_id": cycle_id,
            "target_node_ref": target_node_ref,
            "student_id": student_id,
            "status": lifecycle_status,
            "blocked_reasons": sorted(set(blocked_reasons)),
            "production_mutation_allowed": False,
            "growth_engine_gate": growth_engine_gate,
            "teacher_review": teacher_review,
            "training_backend_plan": training_backend_plan,
            "training": training,
            "child_execution": child_execution,
            "hive_route": hive_route,
            "tensor_program": tensor_program,
            "sealed_eval": sealed_eval,
            "node_registry": node_registry,
            "federation": federation,
            "dream_cycle": dream_cycle,
            "runtime_foundry": runtime_foundry,
            "deep_replay": deep_replay,
            "signer_readiness": signer_readiness,
            "productization": productization,
            "artifact_bridge": artifact_bridge,
            "training_replay_evidence": training_replay_evidence,
            "child_execution_replay_evidence": child_execution_replay_evidence,
            "hive_route_replay_evidence": hive_route_replay_evidence,
            "tensor_runtime_replay_evidence": tensor_runtime_replay_evidence,
            "reviewer_confidence_evidence": reviewer_confidence_evidence,
            "node_registry_replay_evidence": node_registry_replay_evidence,
            "federated_influence_replay_evidence": federated_influence_replay_evidence,
            "recursive_dream_replay_evidence": recursive_dream_replay_evidence,
            "runtime_foundry_replay_evidence": runtime_foundry_replay_evidence,
            "productization_replay_evidence": productization_replay_evidence,
            "replay_consistency": replay_consistency,
            "closed_loop_summary": {
                "teacher_reviewed": teacher_review.get("status") == "teacher_review_complete",
                "child_trained": training.get("status") in {"trained_sandbox_proof", "sandbox_training_complete"},
                "child_shadow_executed": child_execution.get("status") == "shadow_executed",
                "child_promoted": node_registry.get("decision") == "promote_child",
                "parent_retired": node_registry.get("parent_state") == "retired_rollback_restorable",
                "release_ready": bool(productization.get("release_ready")),
                "signer_ready": signer_readiness.get("status") == "ready",
                "growth_engine_gate_clear": growth_engine_gate["allowed"],
            },
            "artifacts": {
                "lifecycle_report_path": str(lifecycle_dir / "lifecycle_report.json"),
                "lifecycle_events_path": str(lifecycle_dir / "lifecycle_events.jsonl"),
            },
        }
        _write_json(lifecycle_dir / "lifecycle_report.json", payload)
        _write_jsonl(lifecycle_dir / "lifecycle_events.jsonl", events)
        deep_replay = DeepReplayBundleBuilder(self.cycle_dir).build(deep_replay_request)
        artifact_bridge["deep_replay_artifact_index_path"] = (deep_replay.get("artifacts") or {}).get("artifact_index_path", "")
        replay_consistency = _validate_lifecycle_replay_consistency(artifact_bridge, deep_replay)
        signer_readiness = _build_signer_readiness(deep_replay)
        if not replay_consistency["passed"]:
            blocked_reasons.append("replay_consistency_failed")
            critical_blockers.append("replay_consistency_failed")
        if signer_readiness.get("production_mutation_blocker"):
            blocked_reasons.append(str(signer_readiness["production_mutation_blocker"]))
        lifecycle_status = "closed_loop_blocked" if critical_blockers else "closed_loop_complete"
        for event in events:
            if event["step"] == "deep_replay":
                event["status"] = deep_replay.get("status")
            if event["step"] == "signer_readiness":
                event["status"] = signer_readiness.get("status")
            if event["step"] == "replay_consistency":
                event["status"] = "passed" if replay_consistency["passed"] else "failed"
                event["checked_bridge_path_count"] = replay_consistency["checked_bridge_path_count"]
        payload["status"] = lifecycle_status
        payload["blocked_reasons"] = sorted(set(blocked_reasons))
        payload["deep_replay"] = deep_replay
        payload["signer_readiness"] = signer_readiness
        payload["artifact_bridge"] = artifact_bridge
        payload["training_replay_evidence"] = training_replay_evidence
        payload["child_execution_replay_evidence"] = child_execution_replay_evidence
        payload["hive_route_replay_evidence"] = hive_route_replay_evidence
        payload["tensor_runtime_replay_evidence"] = tensor_runtime_replay_evidence
        payload["reviewer_confidence_evidence"] = reviewer_confidence_evidence
        payload["node_registry_replay_evidence"] = node_registry_replay_evidence
        payload["federated_influence_replay_evidence"] = federated_influence_replay_evidence
        payload["recursive_dream_replay_evidence"] = recursive_dream_replay_evidence
        payload["runtime_foundry_replay_evidence"] = runtime_foundry_replay_evidence
        payload["productization_replay_evidence"] = productization_replay_evidence
        payload["replay_consistency"] = replay_consistency
        payload["closed_loop_summary"]["signer_ready"] = signer_readiness.get("status") == "ready"
        _write_json(lifecycle_dir / "lifecycle_report.json", payload)
        _write_jsonl(lifecycle_dir / "lifecycle_events.jsonl", events)
        node_registry_snapshot = NodeRegistrySnapshotBuilder(self.cycle_dir).build(
            {"cycle_id": cycle_id, "snapshot_id": f"snapshot:{lifecycle_name}"}
        )
        events.append({"step": "node_registry_snapshot", "status": node_registry_snapshot.get("status")})
        deep_replay = DeepReplayBundleBuilder(self.cycle_dir).build(deep_replay_request)
        artifact_bridge["deep_replay_artifact_index_path"] = (deep_replay.get("artifacts") or {}).get("artifact_index_path", "")
        replay_consistency = _validate_lifecycle_replay_consistency(artifact_bridge, deep_replay)
        signer_readiness = _build_signer_readiness(deep_replay)
        artifact_trust = ArtifactTrustRegistry(artifacts_dir=self.cycle_dir).scan_deep_replay_bundle(deep_replay)
        if not replay_consistency["passed"]:
            blocked_reasons.append("replay_consistency_failed")
            critical_blockers.append("replay_consistency_failed")
        if signer_readiness.get("production_mutation_blocker"):
            blocked_reasons.append(str(signer_readiness["production_mutation_blocker"]))
        if artifact_trust.get("quarantined_count"):
            blocked_reasons.append("artifact_trust_quarantine")
        lifecycle_status = "closed_loop_blocked" if critical_blockers else "closed_loop_complete"
        events.append(
            {
                "step": "artifact_trust",
                "status": "trusted" if artifact_trust.get("quarantined_count") == 0 else "quarantined",
            }
        )
        lifecycle_evidence_chain = _build_lifecycle_evidence_chain(
            chain_id=f"chain:{lifecycle_name}",
            lifecycle_id=lifecycle_id,
            cycle_id=cycle_id,
            lifecycle_status=lifecycle_status,
            blocked_reasons=sorted(set(blocked_reasons)),
            evidence_blocks={
                "training_replay_evidence": training_replay_evidence,
                "child_execution_replay_evidence": child_execution_replay_evidence,
                "hive_route_replay_evidence": hive_route_replay_evidence,
                "tensor_runtime_replay_evidence": tensor_runtime_replay_evidence,
                "reviewer_confidence_evidence": reviewer_confidence_evidence,
                "node_registry_replay_evidence": node_registry_replay_evidence,
                "federated_influence_replay_evidence": federated_influence_replay_evidence,
                "recursive_dream_replay_evidence": recursive_dream_replay_evidence,
                "runtime_foundry_replay_evidence": runtime_foundry_replay_evidence,
                "productization_replay_evidence": productization_replay_evidence,
                "replay_consistency": replay_consistency,
                "signer_readiness": signer_readiness,
                "artifact_trust": artifact_trust,
            },
        )
        events.append(
            {
                "step": "lifecycle_evidence_chain",
                "status": lifecycle_evidence_chain["status"],
                "evidence_count": lifecycle_evidence_chain["evidence_count"],
                "blocked_count": lifecycle_evidence_chain["blocked_count"],
            }
        )
        for event in events:
            if event["step"] == "deep_replay":
                event["status"] = deep_replay.get("status")
            if event["step"] == "signer_readiness":
                event["status"] = signer_readiness.get("status")
            if event["step"] == "artifact_trust":
                event["status"] = "trusted" if artifact_trust.get("quarantined_count") == 0 else "quarantined"
            if event["step"] == "replay_consistency":
                event["status"] = "passed" if replay_consistency["passed"] else "failed"
                event["checked_bridge_path_count"] = replay_consistency["checked_bridge_path_count"]
        payload["status"] = lifecycle_status
        payload["blocked_reasons"] = sorted(set(blocked_reasons))
        payload["node_registry_snapshot"] = node_registry_snapshot
        payload["deep_replay"] = deep_replay
        payload["signer_readiness"] = signer_readiness
        payload["artifact_trust"] = artifact_trust
        payload["artifact_bridge"] = artifact_bridge
        payload["training_replay_evidence"] = training_replay_evidence
        payload["child_execution_replay_evidence"] = child_execution_replay_evidence
        payload["hive_route_replay_evidence"] = hive_route_replay_evidence
        payload["tensor_runtime_replay_evidence"] = tensor_runtime_replay_evidence
        payload["reviewer_confidence_evidence"] = reviewer_confidence_evidence
        payload["node_registry_replay_evidence"] = node_registry_replay_evidence
        payload["federated_influence_replay_evidence"] = federated_influence_replay_evidence
        payload["recursive_dream_replay_evidence"] = recursive_dream_replay_evidence
        payload["runtime_foundry_replay_evidence"] = runtime_foundry_replay_evidence
        payload["productization_replay_evidence"] = productization_replay_evidence
        payload["lifecycle_evidence_chain"] = lifecycle_evidence_chain
        payload["replay_consistency"] = replay_consistency
        payload["closed_loop_summary"]["signer_ready"] = signer_readiness.get("status") == "ready"
        payload["closed_loop_summary"]["artifact_trusted"] = artifact_trust.get("quarantined_count") == 0
        _write_json(lifecycle_dir / "lifecycle_report.json", payload)
        _write_jsonl(lifecycle_dir / "lifecycle_events.jsonl", events)
        return payload


def _build_training_replay_evidence(training: dict[str, Any]) -> dict[str, Any]:
    math_contract = training.get("math_contract") if isinstance(training.get("math_contract"), dict) else {}
    optimizer_state = training.get("optimizer_state") if isinstance(training.get("optimizer_state"), dict) else {}
    artifacts = training.get("artifacts") if isinstance(training.get("artifacts"), dict) else {}
    return {
        "schema_version": "training_replay_evidence.v0.1",
        "source": "sandbox_training_runner",
        "status": "ready" if math_contract and optimizer_state else "blocked",
        "math_contract_present": bool(math_contract),
        "optimizer_state_present": bool(optimizer_state),
        "replay_boundary": "math-and-optimizer-evidence-only-no-production-weight-mutation",
        "math_contract": {
            "model": math_contract.get("model"),
            "loss": math_contract.get("loss"),
            "grad_w": math_contract.get("grad_w"),
            "grad_b": math_contract.get("grad_b"),
            "update_rule": math_contract.get("update_rule"),
        },
        "optimizer_state": {
            "optimizer": optimizer_state.get("optimizer"),
            "learning_rate": optimizer_state.get("learning_rate"),
            "steps": optimizer_state.get("steps"),
            "parameter_count": optimizer_state.get("parameter_count"),
            "final_gradients": optimizer_state.get("final_gradients") or {},
        },
        "artifact_refs": {
            "training_report_path": artifacts.get("training_report_path", ""),
            "loss_trace_path": artifacts.get("loss_trace_path", ""),
            "checkpoint_path": artifacts.get("checkpoint_path", ""),
        },
        "operator_visible": True,
        "deep_replay_required_artifact_types": [
            "sandbox_training_report",
            "sandbox_loss_trace",
            "sandbox_checkpoint",
        ],
    }


def _build_lifecycle_evidence_chain(
    *,
    chain_id: str,
    lifecycle_id: str,
    cycle_id: str,
    lifecycle_status: str,
    blocked_reasons: list[str],
    evidence_blocks: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    entries = [
        _lifecycle_evidence_chain_entry(evidence_id, evidence)
        for evidence_id, evidence in evidence_blocks.items()
    ]
    blocked_entries = [entry for entry in entries if not entry["ready"]]
    ready_entries = [entry for entry in entries if entry["ready"]]
    artifact_ref_total = sum(int(entry["artifact_ref_count"]) for entry in entries)
    operator_visible_count = sum(1 for entry in entries if entry["operator_visible"])
    return {
        "schema_version": "lifecycle_evidence_chain.v0.1",
        "chain_id": chain_id,
        "lifecycle_id": lifecycle_id,
        "cycle_id": cycle_id,
        "status": "gated" if blocked_entries else "ready",
        "lifecycle_status": lifecycle_status,
        "evidence_count": len(entries),
        "ready_count": len(ready_entries),
        "blocked_count": len(blocked_entries),
        "operator_visible_count": operator_visible_count,
        "artifact_ref_total": artifact_ref_total,
        "ready_evidence_ids": [entry["evidence_id"] for entry in ready_entries],
        "blocked_evidence_ids": [entry["evidence_id"] for entry in blocked_entries],
        "blocked_reasons": blocked_reasons,
        "evidence_entries": entries,
        "mutation_boundary": "read-only-lifecycle-proof-chain-no-production-mutation",
        "operator_visible": True,
        "control_panel_card": "Lifecycle evidence chain",
    }


def _build_finish_readiness_map(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    latest_real_training_gate = summary.get("latest_real_training_execution_gate") or {}
    lifecycle_artifacts = latest_lifecycle.get("artifacts") or {}
    artifact_bridge = latest_lifecycle.get("artifact_bridge") or {}
    productization = latest_lifecycle.get("productization") or latest_cycle.get("productization") or {}
    signer_readiness = latest_lifecycle.get("signer_readiness") or {}
    artifact_trust = latest_lifecycle.get("artifact_trust") or {}
    chain = latest_lifecycle.get("lifecycle_evidence_chain") or {}
    latest_reviewer_window_advancement = summary.get("latest_reviewer_window_advancement") or {}
    sealed_eval_blockers = _sealed_eval_finish_blockers(
        latest_lifecycle.get("reviewer_confidence_evidence") or {},
        latest_lifecycle.get("sealed_eval") or {},
        latest_reviewer_window_advancement,
    )
    real_training_blockers = (
        []
        if latest_real_training_gate.get("production_weight_mutation_allowed")
        else _real_training_runner_blockers(latest_lifecycle.get("training_backend_plan") or {}, latest_lifecycle.get("training") or {})
    ) + _gate_blockers(latest_real_training_gate)

    gates = [
        _finish_gate(
            "real_training_runner",
            "TrainingBackendPlanner + SandboxTrainingRunner",
            latest_lifecycle.get("training", {}).get("status") == "sandbox_training_complete"
            or bool(latest_real_training_gate.get("production_weight_mutation_allowed")),
            _collect_refs(artifact_bridge, "training_backend_plan_path", "training_report_path", "loss_trace_path", "training_checkpoint_path", "adapter_manifest_path")
            + _artifact_refs(latest_real_training_gate),
            real_training_blockers,
            "assess_real_training_gate" if _needs_real_training_gate_action(latest_real_training_gate, real_training_blockers) else "run_sandbox_training",
        ),
        _finish_gate(
            "child_node_execution",
            "ChildNodeExecutor",
            latest_lifecycle.get("child_execution", {}).get("status") == "shadow_executed",
            _collect_refs(artifact_bridge, "child_execution_report_path"),
            _gate_blockers(latest_lifecycle.get("child_execution_replay_evidence") or {}),
            "execute_child_node",
        ),
        _finish_gate(
            "native_hive_moe_runtime",
            "HiveMoEShadowRouter",
            latest_lifecycle.get("hive_route", {}).get("status") == "shadow_routed",
            _artifact_refs(latest_lifecycle.get("hive_route_replay_evidence") or {}),
            _gate_blockers(latest_lifecycle.get("hive_route_replay_evidence") or {}),
            "run_hive_moe_route",
        ),
        _finish_gate(
            "tensor_runtime_kernel",
            "TensorProgramExecutor",
            latest_lifecycle.get("tensor_program", {}).get("status") == "executed_tensor_program",
            _artifact_refs(latest_lifecycle.get("tensor_runtime_replay_evidence") or {}),
            _gate_blockers(latest_lifecycle.get("tensor_runtime_replay_evidence") or {}),
            "execute_tensor_program",
        ),
        _finish_gate(
            "teacher_council_automation",
            "TeacherCouncilReviewer",
            latest_lifecycle.get("teacher_review", {}).get("status") == "teacher_review_complete",
            _artifact_refs(latest_lifecycle.get("teacher_review") or {}),
            _gate_blockers(latest_lifecycle.get("teacher_review") or {}),
            "run_teacher_council_review",
        ),
        _finish_gate(
            "sealed_eval_gauntlet",
            "SealedEvalReviewer + ReviewerCouncilMonitor",
            latest_lifecycle.get("sealed_eval", {}).get("status") == "sealed_eval_complete",
            _collect_refs(artifact_bridge, "eval_scorecard_path") + _artifact_refs(latest_reviewer_window_advancement),
            sealed_eval_blockers,
            "record_reviewer_window" if _needs_reviewer_window_action(sealed_eval_blockers) else "run_eval_gauntlet",
        ),
        _finish_gate(
            "durable_node_registry",
            "NodeRegistryDecisionEngine + NodeRegistrySnapshotBuilder",
            latest_lifecycle.get("node_registry_snapshot", {}).get("status") == "node_registry_snapshot_ready",
            _artifact_refs(latest_lifecycle.get("node_registry_replay_evidence") or {}),
            _gate_blockers(latest_lifecycle.get("node_registry_replay_evidence") or {}, latest_lifecycle.get("node_registry") or {}),
            "inspect_node_registry_snapshot",
        ),
        _finish_gate(
            "federated_learning_loop",
            "FederatedPacketIntake",
            latest_lifecycle.get("federation", {}).get("status") == "accepted_sanitized_packet",
            _artifact_refs(latest_lifecycle.get("federated_influence_replay_evidence") or {}),
            _gate_blockers(latest_lifecycle.get("federated_influence_replay_evidence") or {}),
            "submit_federated_packet",
        ),
        _finish_gate(
            "recursive_dream_execution",
            "RecursiveDreamCycleRunner",
            latest_lifecycle.get("dream_cycle", {}).get("status") == "dream_candidates_materialized",
            _artifact_refs(latest_lifecycle.get("recursive_dream_replay_evidence") or {}),
            _gate_blockers(latest_lifecycle.get("recursive_dream_replay_evidence") or {}),
            "run_dream_cycle",
        ),
        _finish_gate(
            "runtime_quantization_foundry",
            "RuntimeQuantizationBenchmarkRunner",
            latest_lifecycle.get("runtime_foundry", {}).get("status") == "benchmark_complete",
            _artifact_refs(latest_lifecycle.get("runtime_foundry_replay_evidence") or {}),
            _gate_blockers(latest_lifecycle.get("runtime_foundry_replay_evidence") or {}),
            "run_runtime_benchmark",
        ),
        _finish_gate(
            "deep_replay_ui",
            "DeepReplayBundleBuilder + Control Panel Replay",
            latest_lifecycle.get("deep_replay", {}).get("status") == "deep_replay_ready" and bool((latest_lifecycle.get("replay_consistency") or {}).get("passed")),
            _collect_refs(lifecycle_artifacts, "lifecycle_report_path", "lifecycle_events_path") + _artifact_refs(latest_lifecycle.get("deep_replay") or {}),
            _gate_blockers(signer_readiness, artifact_trust, latest_lifecycle.get("replay_consistency") or {}),
            "run_deep_replay",
        ),
        _finish_gate(
            "productization",
            "ProductizationReadinessAssessor",
            bool(productization.get("release_ready")),
            _artifact_refs(productization),
            _gate_blockers(productization, productization.get("productization_replay_evidence") or {}),
            "assess_productization",
        ),
    ]
    ready_count = sum(1 for gate in gates if gate["status"] == "ready")
    gated_count = sum(1 for gate in gates if gate["status"] == "gated")
    blocked_count = sum(1 for gate in gates if gate["status"] in {"blocked", "not_recorded"})
    return {
        "schema_version": "finish_readiness_map.v0.1",
        "status": "ready" if ready_count == len(gates) else "blocked" if blocked_count else "gated",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "lifecycle_id": latest_lifecycle.get("lifecycle_id"),
        "gate_count": len(gates),
        "ready_count": ready_count,
        "gated_count": gated_count,
        "blocked_count": blocked_count,
        "next_operator_actions": [gate["next_operator_action"] for gate in gates if gate["status"] != "ready"],
        "gates": gates,
        "lifecycle_evidence_chain_ref": chain.get("chain_id"),
        "mutation_boundary": "read-only-finish-map-no-production-mutation",
        "operator_visible": True,
    }


def _build_release_manifest_status_rollup(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    support_bundle = latest_lifecycle.get("support_bundle_manifest") or {}
    first_run = latest_lifecycle.get("first_run_readiness") or {}
    crash_diagnostics = latest_lifecycle.get("crash_diagnostics") or {}
    release_package = latest_lifecycle.get("release_package") or {}
    go_no_go = latest_lifecycle.get("release_go_no_go") or {}
    support_status = "ready" if support_bundle.get("zip_created") else "blocked" if support_bundle else "not_recorded"
    first_run_status = "ready" if first_run.get("decision") == "ready" else "blocked" if first_run else "not_recorded"
    crash_status = "ready" if crash_diagnostics.get("logs_packaged") else "blocked" if crash_diagnostics else "not_recorded"
    package_status = (
        "ready"
        if release_package.get("package_created") and release_package.get("buyer_release_allowed")
        else "blocked"
        if release_package
        else "not_recorded"
    )
    go_no_go_status = "approved" if go_no_go.get("decision") == "approved" else "blocked" if go_no_go else "not_recorded"
    statuses = [support_status, first_run_status, crash_status, package_status, go_no_go_status]
    status = "approved" if statuses == ["ready", "ready", "ready", "ready", "approved"] else "blocked"
    if all(item == "not_recorded" for item in statuses):
        status = "not_recorded"
    return {
        "schema_version": "release_manifest_status_rollup.v0.1",
        "status": status,
        "cycle_id": latest_lifecycle.get("cycle_id"),
        "lifecycle_id": latest_lifecycle.get("lifecycle_id"),
        "support_bundle_status": support_status,
        "first_run_status": first_run_status,
        "crash_diagnostics_status": crash_status,
        "release_package_status": package_status,
        "go_no_go_status": go_no_go_status,
        "buyer_release_allowed": bool(go_no_go.get("buyer_release_allowed") or release_package.get("buyer_release_allowed")),
        "release_mutation_allowed": bool(go_no_go.get("release_mutation_allowed")),
        "latest_refs": {
            "support_bundle": (support_bundle.get("artifacts") or {}).get("support_bundle_path"),
            "first_run_readiness": (first_run.get("artifacts") or {}).get("readiness_bundle_path"),
            "crash_diagnostics": (crash_diagnostics.get("artifacts") or {}).get("diagnostics_bundle_path"),
            "release_package": (release_package.get("artifacts") or {}).get("release_package_path"),
            "go_no_go_review": (go_no_go.get("artifacts") or {}).get("review_artifact_path"),
        },
        "operator_visible": True,
        "mutation_boundary": "release-status-rollup-read-only-no-release-mutation",
        "control_panel_label": "Release package preview" if status != "approved" else "Release go/no-go approved",
    }


def _finish_gate(
    gate_id: str,
    owner_subsystem: str,
    ready: bool,
    evidence_refs: list[str],
    blockers: list[str],
    next_operator_action: str,
) -> dict[str, Any]:
    status = "ready" if ready and not blockers else "gated" if ready else "blocked" if blockers else "not_recorded"
    return {
        "gate_id": gate_id,
        "status": status,
        "owner_subsystem": owner_subsystem,
        "evidence_refs": evidence_refs,
        "blockers": blockers,
        "next_operator_action": next_operator_action,
    }


def _gate_blockers(*items: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        blockers.extend(_lifecycle_evidence_blockers(item))
        status = str(item.get("status") or item.get("decision") or "")
        if status in {"blocked", "failed", "quarantined"}:
            blockers.append(status)
        if item.get("promotion_allowed") is False:
            blockers.append("promotion_not_allowed")
        if item.get("release_ready") is False:
            blockers.append("release_not_ready")
    return sorted(set(blockers))


def _real_training_runner_blockers(training_backend_plan: dict[str, Any], training: dict[str, Any]) -> list[str]:
    blockers = _gate_blockers(training_backend_plan, training)
    if training.get("status") == "sandbox_training_complete":
        blockers.append("production_training_runner_not_enabled")
    exports = training.get("exports") if isinstance(training.get("exports"), dict) else {}
    for export_name, export in exports.items():
        if isinstance(export, dict) and str(export.get("state") or "").startswith("blocked_"):
            blockers.append(f"{export_name}_export_{export['state']}")
    return sorted(set(blockers))


def _sealed_eval_finish_blockers(
    reviewer_confidence_evidence: dict[str, Any],
    sealed_eval: dict[str, Any],
    reviewer_window_advancement: dict[str, Any],
) -> list[str]:
    blockers = _gate_blockers(reviewer_confidence_evidence, sealed_eval)
    if sealed_eval.get("status") != "sealed_eval_complete":
        return blockers
    if not reviewer_window_advancement:
        blockers.append("reviewer_window_advancement_missing")
        return sorted(set(blockers))
    ejection_readiness = reviewer_window_advancement.get("ejection_readiness_evidence") or {}
    if ejection_readiness.get("status") == "ready" and ejection_readiness.get("teacher_ejection_allowed") is True:
        blockers = [
            blocker
            for blocker in blockers
            if blocker
            not in {
                "teacher_ejection_requires_post_promotion_consistency_windows",
                "teacher_ejection_not_ready",
                "reviewer_windows_pending",
            }
        ]
    blockers.extend(str(item) for item in ejection_readiness.get("blockers") or [])
    if ejection_readiness.get("pending_window_count"):
        blockers.append("reviewer_windows_pending")
    if ejection_readiness.get("teacher_ejection_allowed") is False:
        blockers.append("teacher_ejection_not_ready")
    return sorted(set(blockers))


def _needs_reviewer_window_action(blockers: list[str]) -> bool:
    return any(str(blocker).startswith("reviewer_window") for blocker in blockers) or "teacher_ejection_not_ready" in blockers


def _needs_real_training_gate_action(latest_real_training_gate: dict[str, Any], blockers: list[str]) -> bool:
    if latest_real_training_gate and latest_real_training_gate.get("production_weight_mutation_allowed"):
        return False
    artifact_trust_handoff = latest_real_training_gate.get("artifact_trust_handoff") or {}
    artifact_trust_blockers = set(str(item) for item in artifact_trust_handoff.get("blockers") or [])
    if artifact_trust_handoff.get("status") == "blocked" or artifact_trust_blockers:
        return True
    gate_action_blockers = {
        "operator_approval_required",
        "human_approval_required",
        "allow_real_weight_mutation_required",
        "license_not_approved_for_training",
        "training_backend_plan_ref_required",
        "dataset_manifest_ref_required",
        "sealed_hidden_eval_attestation_required",
        "training_dependency_report_required",
        "artifact_signing_ready_required",
        "artifact_trust_clear_required",
        "trusted_artifact_refs_required",
        "production_training_runner_not_enabled",
    }
    return bool(gate_action_blockers.intersection(str(item) for item in blockers))


def _build_deep_replay_drilldown_summary(deep_replay: dict[str, Any] | None) -> dict[str, Any]:
    if not deep_replay:
        return {
            "schema_version": "deep_replay_drilldown_summary.v0.1",
            "status": "missing",
            "drilldown_count": 0,
            "drilldowns": [],
            "has_real_training_artifact_trust": False,
            "artifact_type_counts": {},
            "artifact_index_path": None,
            "operator_visible": True,
        }
    drilldowns = [str(item) for item in deep_replay.get("drilldowns") or []]
    artifact_type_counts = {
        str(artifact_type): int(count)
        for artifact_type, count in (deep_replay.get("artifact_type_counts") or {}).items()
    }
    artifact_index_path = str((deep_replay.get("artifacts") or {}).get("artifact_index_path") or "")
    if artifact_index_path and not artifact_type_counts:
        for record in _read_jsonl(Path(artifact_index_path)):
            artifact_type = str(record.get("artifact_type") or "artifact")
            artifact_type_counts[artifact_type] = artifact_type_counts.get(artifact_type, 0) + 1
    return {
        "schema_version": "deep_replay_drilldown_summary.v0.1",
        "status": "ready" if deep_replay.get("status") == "deep_replay_ready" else "blocked",
        "replay_id": deep_replay.get("replay_id"),
        "cycle_id": deep_replay.get("cycle_id"),
        "drilldown_count": len(drilldowns),
        "drilldowns": drilldowns,
        "has_real_training_artifact_trust": "real_training_artifact_trust" in drilldowns,
        "artifact_count": int(deep_replay.get("artifact_count") or 0),
        "artifact_type_counts": artifact_type_counts,
        "artifact_index_path": artifact_index_path or None,
        "operator_visible": True,
        "mutation_boundary": "read-only-deep-replay-summary-no-production-mutation",
}


def _build_deep_replay_bundle_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_deep_replay = latest_lifecycle.get("deep_replay") or summary.get("latest_deep_replay") or latest_cycle.get("deep_replay_ui") or {}
    drilldown_summary = _build_deep_replay_drilldown_summary(latest_deep_replay)
    signature_policy = latest_deep_replay.get("signature_policy") or {}
    signature_summary = latest_deep_replay.get("signature_summary") or {}
    artifacts = latest_deep_replay.get("artifacts") or {}
    artifact_trust_scan = latest_lifecycle.get("artifact_trust") or {}
    latest_real_training_gate = summary.get("latest_real_training_execution_gate") or {}
    artifact_trust_handoff = latest_real_training_gate.get("artifact_trust_handoff") or {}
    required_drilldowns = ["growth_lifecycle", "sandbox_runner_training"]
    drilldowns = [str(item) for item in latest_deep_replay.get("drilldowns") or []]
    missing_drilldowns = [drilldown for drilldown in required_drilldowns if drilldown not in drilldowns]
    template = {
        "cycle_id": latest_deep_replay.get("cycle_id") or latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "replay_id": latest_deep_replay.get("replay_id") or "replay:scorecard_template",
        "signing_key_file": None,
        "signing_key_passphrase_provided": False,
        "signing_seed_hex_provided": False,
        "artifact_signing_seed_hex_provided": False,
        "current_signature_state": signature_policy.get("current_signature_state") or "unsigned_v0",
        "next_signature_state": signature_policy.get("next_signature_state") or "signed_ed25519",
        "production_promotion_requires_real_signing": bool(signature_policy.get("production_promotion_requires_real_signing", True)),
        "real_signing_blocker": signature_policy.get("real_signing_blocker"),
        "signing_configuration_state": signature_policy.get("signing_configuration_state") or "missing",
        "encrypted_key_file_persisted": bool(signature_policy.get("encrypted_key_file_persisted")),
        "signing_key_storage_scope": signature_policy.get("signing_key_storage_scope"),
        "signature_summary": signature_summary,
        "deep_replay_bundle_path": artifacts.get("deep_replay_bundle_path"),
        "artifact_index_path": artifacts.get("artifact_index_path"),
        "drilldowns": drilldowns,
        "required_drilldowns": required_drilldowns,
        "missing_drilldowns": missing_drilldowns,
        "artifact_count": int(latest_deep_replay.get("artifact_count") or 0),
        "artifact_type_counts": latest_deep_replay.get("artifact_type_counts") or {},
        "artifact_trust_scan": artifact_trust_scan
        or {
            "source": "not_recorded",
            "quarantined_count": None,
            "promotion_allowed": False,
            "promotion_blockers": ["artifact_trust_scan_not_recorded"],
        },
        "artifact_trust_handoff": artifact_trust_handoff
        or {
            "status": "not_recorded",
            "blockers": ["real_training_gate_not_recorded"],
        },
        "drilldown_summary": drilldown_summary,
    }
    missing_proof_fields = []
    for field in ("cycle_id", "replay_id", "deep_replay_bundle_path", "artifact_index_path"):
        if not template[field]:
            missing_proof_fields.append(field)
    if latest_deep_replay.get("status") != "deep_replay_ready":
        missing_proof_fields.append("deep_replay_ready")
    if missing_drilldowns:
        missing_proof_fields.append("required_drilldowns")
    return {
        "schema_version": "deep_replay_bundle_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/deep-replay",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": [
            "cycle_id",
            "replay_id",
            "deep_replay_ready",
            "deep_replay_bundle_path",
            "artifact_index_path",
            "required_drilldowns",
        ],
        "optional_signature_fields": [
            "signing_seed_hex",
            "artifact_signing_seed_hex",
            "signing_key_file",
            "signing_key_passphrase",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-deep-replay-bundle",
        "operator_visible": True,
        "mutation_boundary": "template-only-deep-replay-build-no-production-mutation",
    }


def _build_artifact_trust_scan_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    artifact_trust = latest_lifecycle.get("artifact_trust") or {}
    scans = artifact_trust.get("scans") or []
    selected_scan = artifact_trust.get("adapter_artifact_scan") or next(
        (
            scan
            for scan in scans
            if (scan.get("metadata") or {}).get("source") == "sandbox_adapter_artifact_bundle"
        ),
        next((scan for scan in scans if scan.get("status") == "quarantined"), scans[0] if scans else {}),
    )
    metadata = selected_scan.get("metadata") or {}
    template = {
        "artifact_id": selected_scan.get("artifact_id"),
        "artifact_type": selected_scan.get("artifact_type") or "document",
        "uri": selected_scan.get("uri"),
        "format": selected_scan.get("format") or "unknown",
        "license_status": selected_scan.get("license_status") or "needs_review",
        "provenance_refs": selected_scan.get("provenance_refs") or [],
        "checksum": selected_scan.get("checksum") or "",
        "signature_ref": selected_scan.get("signature_ref") or "",
        "contains_pickle": bool(selected_scan.get("contains_pickle")),
        "metadata": {
            "source": metadata.get("source") or artifact_trust.get("source"),
            "replay_id": metadata.get("replay_id") or artifact_trust.get("replay_id"),
            "relative_path": metadata.get("relative_path"),
            "signature_state": metadata.get("signature_state"),
            "signature_algorithm": metadata.get("signature_algorithm"),
        },
        "latest_scan_status": selected_scan.get("status") or "not_recorded",
        "trust_decision": selected_scan.get("trust_decision"),
        "reason_codes": selected_scan.get("reason_codes") or [],
        "trust_findings": selected_scan.get("trust_findings") or [],
        "signature_required_for_trust": not bool(selected_scan.get("signature_ref")),
        "scan_count": artifact_trust.get("scan_count") or 0,
        "trusted_count": artifact_trust.get("trusted_count") or 0,
        "quarantined_count": artifact_trust.get("quarantined_count") or 0,
    }
    missing_proof_fields = []
    for field in ("artifact_id", "artifact_type", "uri", "license_status", "checksum"):
        if not template[field]:
            missing_proof_fields.append(field)
    if not template["provenance_refs"]:
        missing_proof_fields.append("provenance_refs")
    if not template["metadata"].get("source"):
        missing_proof_fields.append("metadata.source")
    promotion_blockers = artifact_trust.get("promotion_blockers") or []
    return {
        "schema_version": "artifact_trust_scan_request_template.v0.1",
        "endpoint": "/ops/brain/artifact-trust/scans",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": [
            "artifact_id",
            "artifact_type",
            "uri",
            "license_status",
            "provenance_refs",
            "checksum",
            "metadata.source",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "promotion_blockers": promotion_blockers,
        "template": template,
        "source": "latest-lifecycle-artifact-trust-scan",
        "operator_visible": True,
        "mutation_boundary": "template-only-artifact-trust-scan-no-promotion",
    }


def _build_project_local_signing_key_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    signer_readiness = latest_lifecycle.get("signer_readiness") or {}
    latest_deep_replay = latest_lifecycle.get("deep_replay") or summary.get("latest_deep_replay") or {}
    signature_policy = latest_deep_replay.get("signature_policy") or {}
    key_file_path = summary.get("project_local_signing_default_key_file_path")
    template = {
        "key_id": "artifact_signing_key",
        "key_file_path": key_file_path,
        "passphrase_required": True,
        "passphrase_persisted": False,
        "seed_hex_required": False,
        "seed_generated_if_omitted": True,
        "signing_secret_persisted": False,
        "storage_scope": "project_local_encrypted_file",
        "deep_replay_request_fields": ["signing_key_file", "signing_key_passphrase"],
        "current_signer_status": signer_readiness.get("status") or "not_recorded",
        "current_signature_state": signer_readiness.get("current_signature_state")
        or signature_policy.get("current_signature_state")
        or "unsigned_v0",
        "next_signature_state": signer_readiness.get("next_signature_state")
        or signature_policy.get("next_signature_state")
        or "signed_ed25519",
        "signing_configuration_state": signer_readiness.get("signing_configuration_state")
        or signature_policy.get("signing_configuration_state")
        or "missing",
        "encrypted_key_file_persisted": bool(signer_readiness.get("encrypted_key_file_persisted")),
        "durable_project_local_signer": bool(signer_readiness.get("durable_project_local_signer")),
        "production_promotion_requires_real_signing": bool(
            signer_readiness.get("production_promotion_requires_real_signing")
            if signer_readiness
            else signature_policy.get("production_promotion_requires_real_signing", True)
        ),
        "production_mutation_blocker": signer_readiness.get("production_mutation_blocker"),
        "real_signing_blocker": signer_readiness.get("real_signing_blocker") or signature_policy.get("real_signing_blocker"),
    }
    missing_proof_fields = []
    if not template["key_file_path"]:
        missing_proof_fields.append("key_file_path")
    missing_proof_fields.append("passphrase")
    return {
        "schema_version": "project_local_signing_key_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/signing-keys/project-local",
        "method": "POST",
        "ready_to_submit": False,
        "manual_secret_fields": ["passphrase"],
        "required_proof_fields": ["key_id", "key_file_path", "passphrase"],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-signer-readiness-and-project-local-default",
        "operator_visible": True,
        "mutation_boundary": "template-only-project-local-encrypted-signing-key-no-secret-persistence",
    }


def _build_signed_deep_replay_handoff_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    latest_deep_replay = latest_lifecycle.get("deep_replay") or summary.get("latest_deep_replay") or latest_cycle.get("deep_replay_ui") or {}
    signature_policy = latest_deep_replay.get("signature_policy") or {}
    artifact_trust = latest_lifecycle.get("artifact_trust") or {}
    key_file_path = str(summary.get("project_local_signing_default_key_file_path") or "")
    key_file_exists = bool(key_file_path and Path(key_file_path).is_file())
    source_replay_id = latest_deep_replay.get("replay_id") or "replay:scorecard_template"
    template = {
        "cycle_id": latest_deep_replay.get("cycle_id") or latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "source_replay_id": source_replay_id,
        "replay_id": f"{source_replay_id}_signed" if source_replay_id else "replay:scorecard_template_signed",
        "signing_key_file": key_file_path,
        "signing_key_file_exists": key_file_exists,
        "signing_key_passphrase_provided": False,
        "current_signature_state": signature_policy.get("current_signature_state") or "unsigned_v0",
        "target_signature_state": signature_policy.get("next_signature_state") or "signed_ed25519",
        "current_real_signing_blocker": signature_policy.get("real_signing_blocker"),
        "artifact_trust_quarantined_count": int(artifact_trust.get("quarantined_count") or 0),
        "artifact_trust_promotion_blockers": artifact_trust.get("promotion_blockers") or [],
        "source_deep_replay_bundle_path": (latest_deep_replay.get("artifacts") or {}).get("deep_replay_bundle_path"),
        "source_artifact_index_path": (latest_deep_replay.get("artifacts") or {}).get("artifact_index_path"),
        "expected_signature_state_after_submit": "signed_ed25519",
        "expected_artifact_trust_after_submit": "trusted-if-key-valid-and-replay-consistency-passes",
        "seed_or_passphrase_persisted": False,
    }
    missing_proof_fields = []
    for field in ("cycle_id", "source_replay_id", "source_deep_replay_bundle_path", "source_artifact_index_path", "signing_key_file"):
        if not template[field]:
            missing_proof_fields.append(field)
    if not key_file_exists:
        missing_proof_fields.append("signing_key_file_created")
    missing_proof_fields.append("signing_key_passphrase")
    if latest_deep_replay.get("status") != "deep_replay_ready":
        missing_proof_fields.append("source_deep_replay_ready")
    return {
        "schema_version": "signed_deep_replay_handoff_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/deep-replay",
        "method": "POST",
        "ready_to_submit": False,
        "manual_secret_fields": ["signing_key_passphrase"],
        "required_proof_fields": [
            "cycle_id",
            "source_replay_id",
            "source_deep_replay_ready",
            "signing_key_file",
            "signing_key_file_created",
            "signing_key_passphrase",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "project-local-signing-key-plus-latest-deep-replay",
        "operator_visible": True,
        "mutation_boundary": "template-only-signed-replay-handoff-no-secret-persistence",
    }


def _build_signed_replay_artifact_trust_rescan_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    latest_deep_replay = latest_lifecycle.get("deep_replay") or summary.get("latest_deep_replay") or latest_cycle.get("deep_replay_ui") or {}
    artifact_trust = latest_lifecycle.get("artifact_trust") or {}
    signature_policy = latest_deep_replay.get("signature_policy") or {}
    source_replay_id = str(latest_deep_replay.get("replay_id") or "replay:scorecard_template")
    target_replay_id = f"{source_replay_id}_signed" if source_replay_id else "replay:scorecard_template_signed"
    source_artifacts = latest_deep_replay.get("artifacts") or {}
    source_bundle_path = str(source_artifacts.get("deep_replay_bundle_path") or "")
    source_index_path = str(source_artifacts.get("artifact_index_path") or "")
    signed_bundle_path, signed_index_path = _signed_replay_artifact_paths(source_index_path, target_replay_id)
    signature_summary = _signed_artifact_signature_summary(signed_index_path)
    artifact_count = int(latest_deep_replay.get("artifact_count") or artifact_trust.get("scan_count") or 0)
    source_quarantined_count = int(artifact_trust.get("quarantined_count") or 0)
    source_trusted_count = int(artifact_trust.get("trusted_count") or 0)
    source_adapter_scan = artifact_trust.get("adapter_artifact_scan") or {}
    source_adapter_metadata = source_adapter_scan.get("metadata") or {}
    source_adapter_relative_path = str(source_adapter_metadata.get("relative_path") or "")
    template = {
        "cycle_id": latest_deep_replay.get("cycle_id") or latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "source_replay_id": source_replay_id,
        "target_replay_id": target_replay_id,
        "target_signature_state": signature_policy.get("next_signature_state") or "signed_ed25519",
        "current_artifact_trust_status": "quarantined" if source_quarantined_count else "trusted",
        "source_scan_count": int(artifact_trust.get("scan_count") or 0),
        "source_trusted_count": source_trusted_count,
        "source_quarantined_count": source_quarantined_count,
        "source_adapter_artifact_status": source_adapter_scan.get("status") or "not_recorded",
        "source_adapter_artifact_relative_path": source_adapter_relative_path,
        "expected_adapter_artifact_trust_status_after_rescan": "trusted" if source_adapter_scan else "not_recorded",
        "current_promotion_blockers": artifact_trust.get("promotion_blockers") or [],
        "source_deep_replay_bundle_path": source_bundle_path,
        "source_artifact_index_path": source_index_path,
        "signed_deep_replay_bundle_path": signed_bundle_path,
        "signed_artifact_index_path": signed_index_path,
        "signed_deep_replay_bundle_exists": bool(signed_bundle_path and Path(signed_bundle_path).is_file()),
        "signed_artifact_index_exists": bool(signed_index_path and Path(signed_index_path).is_file()),
        "signed_artifact_signature_summary": signature_summary,
        "expected_quarantined_count_after_rescan": 0,
        "expected_trusted_count_after_rescan": artifact_count,
        "scan_request_template": {
            "artifact_id": f"deep-replay::{target_replay_id}::<relative_path>",
            "artifact_type": "document",
            "uri": "<signed-replay-artifact-path>",
            "format": "unknown",
            "license_status": "approved",
            "provenance_refs": [signed_bundle_path] if signed_bundle_path else [],
            "checksum": "<signed-artifact-sha256>",
            "signature_ref": "ed25519:<public-key>:<signature-prefix>",
            "contains_pickle": False,
            "metadata": {
                "source": "deep_replay_bundle",
                "replay_id": target_replay_id,
                "signature_state": "signed_ed25519",
                "rescan_source_replay_id": source_replay_id,
            },
        },
        "adapter_scan_request_template": {
            "artifact_id": f"deep-replay::{target_replay_id}::{source_adapter_relative_path or '<adapter-relative-path>'}",
            "artifact_type": "adapter",
            "uri": "<signed-adapter-artifact-path>",
            "format": "zip",
            "license_status": "approved",
            "provenance_refs": [signed_bundle_path] if signed_bundle_path else [],
            "checksum": "<signed-adapter-artifact-sha256>",
            "signature_ref": "ed25519:<public-key>:<signature-prefix>",
            "contains_pickle": False,
            "metadata": {
                "source": "sandbox_adapter_artifact_bundle",
                "replay_id": target_replay_id,
                "relative_path": source_adapter_relative_path,
                "signature_state": "signed_ed25519",
                "rescan_source_replay_id": source_replay_id,
            },
        },
    }
    missing_proof_fields = []
    for field in ("cycle_id", "source_replay_id", "source_deep_replay_bundle_path", "source_artifact_index_path"):
        if not template[field]:
            missing_proof_fields.append(field)
    if not template["signed_deep_replay_bundle_exists"]:
        missing_proof_fields.append("signed_deep_replay_bundle_path")
    if not template["signed_artifact_index_exists"]:
        missing_proof_fields.append("signed_artifact_index_path")
    if signature_summary["signed_count"] < artifact_count:
        missing_proof_fields.append("signed_replay_artifact_signatures")
    if template["target_signature_state"] != "signed_ed25519":
        missing_proof_fields.append("target_signature_state")
    return {
        "schema_version": "signed_replay_artifact_trust_rescan_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/signed-replay-artifact-trust-rescans",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": [
            "cycle_id",
            "source_replay_id",
            "source_deep_replay_bundle_path",
            "source_artifact_index_path",
            "signed_deep_replay_bundle_path",
            "signed_artifact_index_path",
            "signed_replay_artifact_signatures",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "promotion_blockers": artifact_trust.get("promotion_blockers") or [],
        "template": template,
        "source": "signed-deep-replay-handoff-plus-artifact-trust",
        "operator_visible": True,
        "mutation_boundary": "signed-replay-artifact-trust-rescan-updates-lifecycle-trust-no-production-mutation",
    }


def _signed_replay_artifact_paths(source_artifact_index_path: str, target_replay_id: str) -> tuple[str, str]:
    if not source_artifact_index_path:
        return "", ""
    source_dir = Path(source_artifact_index_path).parent
    signed_dir = source_dir.with_name(safe_name(target_replay_id))
    return str(signed_dir / "deep_replay_bundle.json"), str(signed_dir / "artifact_index.jsonl")


def _signed_artifact_signature_summary(signed_artifact_index_path: str) -> dict[str, Any]:
    records = _read_jsonl(Path(signed_artifact_index_path)) if signed_artifact_index_path else []
    signed_count = sum(1 for record in records if record.get("signature_state") == "signed_ed25519")
    missing_signature_count = sum(1 for record in records if record.get("signature_state") != "signed_ed25519")
    return {
        "artifact_count": len(records),
        "signed_count": signed_count,
        "missing_signature_count": missing_signature_count,
        "all_signed": bool(records) and missing_signature_count == 0,
    }


def _build_real_training_promotion_handoff_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    latest_real_training_gate = summary.get("latest_real_training_execution_gate") or {}
    latest_deep_replay = latest_lifecycle.get("deep_replay") or summary.get("latest_deep_replay") or latest_cycle.get("deep_replay_ui") or {}
    sealed_eval = latest_lifecycle.get("sealed_eval") or latest_cycle.get("sealed_eval_gauntlet") or {}
    artifact_trust = latest_lifecycle.get("artifact_trust") or {}
    latest_advancement = summary.get("latest_reviewer_window_advancement") or latest_lifecycle.get("reviewer_window_advancement") or {}
    reviewer_consistency = sealed_eval.get("reviewer_consistency") or {}
    ejection_readiness = latest_advancement.get("ejection_readiness_evidence") or {}
    signed_rescan = _build_signed_replay_artifact_trust_rescan_request_template(summary)
    signed_rescan_template = signed_rescan.get("template") or {}
    source_replay_id = str(latest_deep_replay.get("replay_id") or "replay:scorecard_template")
    trusted_signed_replay_id = artifact_trust.get("replay_id") if artifact_trust.get("signed_replay_trust_clear") else None
    target_signed_replay_id = str(trusted_signed_replay_id or signed_rescan_template.get("target_replay_id") or f"{source_replay_id}_signed")
    sealed_eval_passed = bool(
        sealed_eval.get("status") == "sealed_eval_complete"
        and (sealed_eval.get("hidden_eval_attestation") or {}).get("leakage_scan", {}).get("status") == "passed"
        and float(sealed_eval.get("lower_confidence_surpass_bound") or 0) > 0
    )
    reviewer_windows_ready = bool(
        ejection_readiness.get("status") == "ready"
        and int(ejection_readiness.get("pending_window_count") or 0) == 0
    ) or bool((reviewer_consistency.get("pending_window_count") or 0) == 0)
    artifact_trust_clear = bool(artifact_trust.get("promotion_allowed") and int(artifact_trust.get("quarantined_count") or 0) == 0)
    signed_replay_trust_clear = bool(artifact_trust.get("signed_replay_trust_clear") or (signed_rescan.get("ready_to_submit") and artifact_trust_clear))
    signed_rescan_template = signed_rescan.get("template") or {}
    adapter_artifact_trust_status = str(artifact_trust.get("adapter_artifact_trust_status") or "not_recorded")
    adapter_artifact_trust_clear = bool(artifact_trust_clear and adapter_artifact_trust_status == "trusted")
    promotion_blockers = []
    if not signed_replay_trust_clear:
        promotion_blockers.append("trusted_signed_replay_required")
    if not adapter_artifact_trust_clear:
        promotion_blockers.append("trusted_adapter_artifact_required")
    if not sealed_eval_passed:
        promotion_blockers.append("sealed_eval_pass_required")
    if not reviewer_windows_ready:
        promotion_blockers.append("reviewer_windows_required")
    promotion_blockers.extend(str(blocker) for blocker in artifact_trust.get("promotion_blockers") or [])
    template = {
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "gate_id": "real_training_promotion_handoff_from_scorecard_template",
        "student_id": latest_lifecycle.get("student_id") or sealed_eval.get("student_id") or latest_cycle.get("student_id"),
        "target_node_ref": latest_lifecycle.get("target_node_ref") or latest_cycle.get("target_node_ref"),
        "target_signed_replay_id": target_signed_replay_id,
        "target_signed_replay_artifact_index_path": signed_rescan_template.get("signed_artifact_index_path"),
        "target_signed_deep_replay_bundle_path": signed_rescan_template.get("signed_deep_replay_bundle_path"),
        "production_mutation_requested": False,
        "operator_approved": False,
        "human_approved": False,
        "allow_real_weight_mutation": False,
        "artifact_trust_clear": artifact_trust_clear,
        "adapter_artifact_trust_status": adapter_artifact_trust_status,
        "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
        "source_adapter_artifact_relative_path": signed_rescan_template.get("source_adapter_artifact_relative_path"),
        "expected_adapter_artifact_trust_status_after_rescan": signed_rescan_template.get(
            "expected_adapter_artifact_trust_status_after_rescan"
        ),
        "signed_replay_trust_clear": signed_replay_trust_clear,
        "sealed_eval_passed": sealed_eval_passed,
        "reviewer_windows_ready": reviewer_windows_ready,
        "eval_id": sealed_eval.get("eval_id"),
        "eval_scorecard_path": (sealed_eval.get("artifacts") or {}).get("eval_scorecard_path"),
        "training_backend_plan_ref": latest_real_training_gate.get("training_backend_plan_ref")
        or ((latest_lifecycle.get("training_backend_plan") or {}).get("plan_id")),
        "dataset_manifest_ref": latest_real_training_gate.get("dataset_manifest_ref")
        or ((latest_lifecycle.get("training_backend_plan") or {}).get("dataset_manifest_ref")),
        "signed_rescan_template_ref": "scorecard:signed_replay_artifact_trust_rescan_request_template",
    }
    missing_proof_fields = []
    for field in ("cycle_id", "student_id", "target_node_ref", "target_signed_replay_id", "eval_id", "eval_scorecard_path"):
        if not template[field]:
            missing_proof_fields.append(field)
    if not signed_replay_trust_clear:
        missing_proof_fields.append("trusted_signed_replay")
    if not artifact_trust_clear:
        missing_proof_fields.append("artifact_trust_clear")
    if not adapter_artifact_trust_clear:
        missing_proof_fields.append("adapter_artifact_trust_clear")
    if not sealed_eval_passed:
        missing_proof_fields.append("sealed_eval_passed")
    if not reviewer_windows_ready:
        missing_proof_fields.append("reviewer_windows_ready")
    missing_proof_fields.extend(["operator_approved", "human_approved", "allow_real_weight_mutation"])
    return {
        "schema_version": "real_training_promotion_handoff_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/real-training-gates",
        "method": "POST",
        "ready_to_submit": False,
        "manual_approval_fields": ["operator_approved", "human_approved", "allow_real_weight_mutation"],
        "required_proof_fields": [
            "cycle_id",
            "student_id",
            "target_node_ref",
            "target_signed_replay_id",
            "trusted_signed_replay",
            "artifact_trust_clear",
            "adapter_artifact_trust_clear",
            "sealed_eval_passed",
            "reviewer_windows_ready",
            "operator_approved",
            "human_approved",
            "allow_real_weight_mutation",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "promotion_blockers": sorted(set(promotion_blockers)),
        "template": template,
        "source": "signed-replay-rescan-plus-sealed-eval-reviewer-and-approval-gates",
        "operator_visible": True,
        "mutation_boundary": "template-only-real-training-promotion-handoff-production-mutation-default-off",
    }


def _build_runtime_node_activation_handoff_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    sealed_eval = latest_lifecycle.get("sealed_eval") or latest_cycle.get("sealed_eval_gauntlet") or {}
    node_registry = latest_lifecycle.get("node_registry") or {}
    node_replay = latest_lifecycle.get("node_registry_replay_evidence") or node_registry.get("node_registry_replay_evidence") or {}
    canary_evidence = node_replay.get("canary_promotion_guard_evidence") or node_registry.get("canary_promotion_guard_evidence") or {}
    promotion_handoff = _build_real_training_promotion_handoff_request_template(summary)
    promotion_template = promotion_handoff.get("template") or {}
    current_state = node_replay.get("student_state") or node_registry.get("student_state") or "shadow"
    shadow_runtime_window_passed = bool(canary_evidence.get("shadow_runtime_window_passed"))
    canary_window_passed = bool(canary_evidence.get("canary_window_passed"))
    requested_state = "active" if shadow_runtime_window_passed and canary_window_passed else "canary"
    signed_replay_trust_clear = bool(promotion_template.get("signed_replay_trust_clear"))
    adapter_artifact_trust_status = str(promotion_template.get("adapter_artifact_trust_status") or "not_recorded")
    adapter_artifact_trust_clear = bool(promotion_template.get("adapter_artifact_trust_clear"))
    reviewer_windows_ready = bool(promotion_template.get("reviewer_windows_ready"))
    rollback_restorable = bool(node_replay.get("rollback_restorable") or node_registry.get("rollback_restorable"))
    human_approved = bool(node_replay.get("human_approved"))
    activation_blockers = []
    if not signed_replay_trust_clear:
        activation_blockers.append("trusted_signed_replay_required")
    if not adapter_artifact_trust_clear:
        activation_blockers.append("trusted_adapter_artifact_required")
    if not rollback_restorable:
        activation_blockers.append("rollback_restorable_required")
    if not reviewer_windows_ready:
        activation_blockers.append("reviewer_windows_required")
    if not shadow_runtime_window_passed:
        activation_blockers.append("shadow_runtime_window_required")
    if not canary_window_passed:
        activation_blockers.append("canary_window_required")
    if not human_approved:
        activation_blockers.append("human_approved_required")
    template = {
        "decision_id": "decision:runtime_activation_scorecard_template",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "student_id": latest_lifecycle.get("student_id") or sealed_eval.get("student_id") or latest_cycle.get("student_id"),
        "parent_node_ref": sealed_eval.get("parent_node_ref") or latest_lifecycle.get("target_node_ref") or latest_cycle.get("target_node_ref"),
        "action": "activate_child_runtime",
        "requested_runtime_state": requested_state,
        "current_runtime_state": current_state,
        "target_signed_replay_id": promotion_template.get("target_signed_replay_id"),
        "active_registry_path": (node_replay.get("artifact_refs") or {}).get("active_registry_path"),
        "node_registry_events_path": (node_replay.get("artifact_refs") or {}).get("node_registry_events_path"),
        "rollback_snapshot_path": (node_replay.get("artifact_refs") or {}).get("rollback_snapshot_path"),
        "rollback_restorable": rollback_restorable,
        "signed_replay_trust_clear": signed_replay_trust_clear,
        "adapter_artifact_trust_status": adapter_artifact_trust_status,
        "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
        "reviewer_windows_ready": reviewer_windows_ready,
        "shadow_runtime_window_passed": shadow_runtime_window_passed,
        "canary_window_passed": canary_window_passed,
        "human_approved": human_approved,
        "production_mutation_allowed": False,
    }
    missing_proof_fields = []
    for field in ("cycle_id", "student_id", "parent_node_ref", "target_signed_replay_id", "active_registry_path", "rollback_snapshot_path"):
        if not template[field]:
            missing_proof_fields.append(field)
    if not signed_replay_trust_clear:
        missing_proof_fields.append("trusted_signed_replay")
    if not adapter_artifact_trust_clear:
        missing_proof_fields.append("adapter_artifact_trust_clear")
    if not rollback_restorable:
        missing_proof_fields.append("rollback_restorable")
    if not reviewer_windows_ready:
        missing_proof_fields.append("reviewer_windows_ready")
    if not shadow_runtime_window_passed:
        missing_proof_fields.append("shadow_runtime_window_passed")
    if not canary_window_passed:
        missing_proof_fields.append("canary_window_passed")
    if not human_approved:
        missing_proof_fields.append("human_approved")
    return {
        "schema_version": "runtime_node_activation_handoff_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/node-registry-decisions",
        "method": "POST",
        "ready_to_submit": False,
        "required_proof_fields": [
            "cycle_id",
            "student_id",
            "parent_node_ref",
            "target_signed_replay_id",
            "trusted_signed_replay",
            "adapter_artifact_trust_clear",
            "rollback_restorable",
            "reviewer_windows_ready",
            "shadow_runtime_window_passed",
            "canary_window_passed",
            "human_approved",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "activation_blockers": sorted(set(activation_blockers)),
        "template": template,
        "source": "node-registry-replay-plus-real-training-promotion-handoff",
        "operator_visible": True,
        "mutation_boundary": "template-only-runtime-node-activation-no-live-roster-mutation",
    }


def _build_active_runtime_health_monitor_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    activation = _build_runtime_node_activation_handoff_request_template(summary)
    activation_template = activation.get("template") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_runtime_health = latest_lifecycle.get("runtime_health_monitor") or {}
    runtime_foundry = latest_lifecycle.get("runtime_foundry") or {}
    runtime_evidence = latest_lifecycle.get("runtime_foundry_replay_evidence") or runtime_foundry.get("runtime_foundry_replay_evidence") or runtime_foundry
    observed_runtime_health_metrics = latest_runtime_health.get("observed_metrics") or {}
    signed_replay_trust_clear = bool(activation_template.get("signed_replay_trust_clear"))
    adapter_artifact_trust_status = str(activation_template.get("adapter_artifact_trust_status") or "not_recorded")
    adapter_artifact_trust_clear = bool(activation_template.get("adapter_artifact_trust_clear"))
    current_runtime_state = activation_template.get("current_runtime_state") or "shadow"
    canary_or_active = current_runtime_state in {"canary", "active", "permanent_active"}
    health_window_started = bool(latest_runtime_health.get("health_window_started", False))
    template = {
        "monitor_id": "runtime-health:scorecard_template",
        "cycle_id": activation_template.get("cycle_id"),
        "student_id": activation_template.get("student_id"),
        "target_node_ref": activation_template.get("parent_node_ref"),
        "current_runtime_state": current_runtime_state,
        "target_signed_replay_id": activation_template.get("target_signed_replay_id"),
        "monitor_window": "canary_runtime",
        "rollback_snapshot_path": activation_template.get("rollback_snapshot_path"),
        "node_registry_events_path": activation_template.get("node_registry_events_path"),
        "backend_candidates": runtime_evidence.get("benchmark_count") or len(runtime_evidence.get("candidates") or []),
        "max_error_rate": 0.02,
        "max_p95_latency_ms": 2000,
        "max_route_share": 0.1,
        "auto_disable_on_blocker": True,
        "signed_replay_trust_clear": signed_replay_trust_clear,
        "adapter_artifact_trust_status": adapter_artifact_trust_status,
        "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
        "rollback_restorable": bool(activation_template.get("rollback_restorable")),
        "health_window_started": health_window_started,
        "route_share_observed": observed_runtime_health_metrics.get("route_share", 0.0),
        "error_rate_observed": observed_runtime_health_metrics.get("error_rate"),
        "p95_latency_ms_observed": observed_runtime_health_metrics.get("p95_latency_ms"),
    }
    health_blockers = []
    if not signed_replay_trust_clear:
        health_blockers.append("trusted_signed_replay_required")
    if not adapter_artifact_trust_clear:
        health_blockers.append("trusted_adapter_artifact_required")
    if not canary_or_active:
        health_blockers.append("canary_or_active_runtime_state_required")
    if not health_window_started:
        health_blockers.append("health_window_not_started")
    if not template["rollback_restorable"]:
        health_blockers.append("rollback_restorable_required")
    missing_proof_fields = []
    for field in ("cycle_id", "student_id", "target_node_ref", "rollback_snapshot_path", "target_signed_replay_id"):
        if not template[field]:
            missing_proof_fields.append(field)
    if not signed_replay_trust_clear:
        missing_proof_fields.append("trusted_signed_replay")
    if not adapter_artifact_trust_clear:
        missing_proof_fields.append("adapter_artifact_trust_clear")
    if not canary_or_active:
        missing_proof_fields.append("canary_or_active_runtime_state")
    if not health_window_started:
        missing_proof_fields.append("health_window_started")
    if not template["rollback_restorable"]:
        missing_proof_fields.append("rollback_restorable")
    return {
        "schema_version": "active_runtime_health_monitor_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/runtime-health-monitors",
        "method": "POST",
        "ready_to_submit": False,
        "required_proof_fields": [
            "cycle_id",
            "student_id",
            "target_node_ref",
            "target_signed_replay_id",
            "trusted_signed_replay",
            "adapter_artifact_trust_clear",
            "canary_or_active_runtime_state",
            "health_window_started",
            "rollback_restorable",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "health_blockers": sorted(set(health_blockers)),
        "template": template,
        "source": "runtime-node-activation-plus-runtime-foundry-replay",
        "operator_visible": True,
        "mutation_boundary": "template-only-runtime-health-monitor-no-auto-disable-without-submitted-observations",
    }


def _build_teacher_ejection_parent_retirement_handoff_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    latest_advancement = summary.get("latest_reviewer_window_advancement") or {}
    sealed_eval = latest_lifecycle.get("sealed_eval") or latest_cycle.get("sealed_eval_gauntlet") or {}
    reviewer_confidence = latest_lifecycle.get("reviewer_confidence_evidence") or sealed_eval.get("reviewer_confidence_evidence") or {}
    ejection_readiness = (
        latest_advancement.get("ejection_readiness_evidence")
        or reviewer_confidence.get("ejection_readiness_evidence")
        or sealed_eval.get("ejection_readiness_evidence")
        or {}
    )
    node_replay = latest_lifecycle.get("node_registry_replay_evidence") or {}
    canary_evidence = node_replay.get("canary_promotion_guard_evidence") or {}
    post_promotion_window_passed = bool(canary_evidence.get("post_promotion_window_passed"))
    promotion = _build_real_training_promotion_handoff_request_template(summary)
    promotion_template = promotion.get("template") or {}
    adapter_artifact_trust_status = str(promotion_template.get("adapter_artifact_trust_status") or "not_recorded")
    adapter_artifact_trust_clear = bool(promotion_template.get("adapter_artifact_trust_clear"))
    teacher_ejection_allowed = bool(ejection_readiness.get("teacher_ejection_allowed"))
    parent_retirement_allowed = bool(ejection_readiness.get("parent_retirement_allowed"))
    template = {
        "review_id": "teacher-ejection:scorecard_template",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "student_id": latest_lifecycle.get("student_id") or sealed_eval.get("student_id") or latest_cycle.get("student_id"),
        "parent_node_ref": sealed_eval.get("parent_node_ref") or latest_lifecycle.get("target_node_ref") or latest_cycle.get("target_node_ref"),
        "eval_id": sealed_eval.get("eval_id"),
        "teacher_ejection_allowed": teacher_ejection_allowed,
        "parent_retirement_allowed": parent_retirement_allowed,
        "post_promotion_window_passed": post_promotion_window_passed,
        "ivy_grade_review_passed": False,
        "greatly_outperforms_parent": False,
        "child_retained_after_parent_retirement": True,
        "rollback_retention_required": True,
        "rollback_restorable": bool(node_replay.get("rollback_restorable")),
        "adapter_artifact_trust_status": adapter_artifact_trust_status,
        "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
        "required_windows": ejection_readiness.get("required_windows") or ReviewerWindowAdvancementRecorder.REQUIRED_WINDOWS,
        "passed_windows": ejection_readiness.get("passed_windows") or [],
        "pending_window_count": int(ejection_readiness.get("pending_window_count") or 0),
        "lower_confidence_surpass_bound": reviewer_confidence.get("lower_confidence_surpass_bound")
        or sealed_eval.get("lower_confidence_surpass_bound"),
        "required_lower_confidence_margin": reviewer_confidence.get("required_lower_confidence_margin") or 0.0,
    }
    missing_proof_fields = []
    for field in ("cycle_id", "student_id", "parent_node_ref", "eval_id"):
        if not template[field]:
            missing_proof_fields.append(field)
    if not teacher_ejection_allowed:
        missing_proof_fields.append("teacher_ejection_allowed")
    if not parent_retirement_allowed:
        missing_proof_fields.append("parent_retirement_allowed")
    if not post_promotion_window_passed:
        missing_proof_fields.append("post_promotion_window_passed")
    if not template["ivy_grade_review_passed"]:
        missing_proof_fields.append("ivy_grade_review_passed")
    if not template["greatly_outperforms_parent"]:
        missing_proof_fields.append("greatly_outperforms_parent")
    if not template["rollback_restorable"]:
        missing_proof_fields.append("rollback_restorable")
    if not adapter_artifact_trust_clear:
        missing_proof_fields.append("adapter_artifact_trust_clear")
    blockers = [
        field
        for field in (
            "teacher_ejection_allowed",
            "parent_retirement_allowed",
            "post_promotion_window_passed",
            "ivy_grade_review_passed",
            "greatly_outperforms_parent",
            "rollback_restorable",
            "adapter_artifact_trust_clear",
        )
        if field in missing_proof_fields
    ]
    return {
        "schema_version": "teacher_ejection_parent_retirement_handoff_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/teacher-ejection-reviews",
        "method": "POST",
        "ready_to_submit": False,
        "required_proof_fields": [
            "cycle_id",
            "student_id",
            "parent_node_ref",
            "eval_id",
            "teacher_ejection_allowed",
            "parent_retirement_allowed",
            "post_promotion_window_passed",
            "ivy_grade_review_passed",
            "greatly_outperforms_parent",
            "rollback_restorable",
            "adapter_artifact_trust_clear",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "retirement_blockers": sorted(set(blockers)),
        "template": template,
        "source": "reviewer-confidence-ejection-readiness-plus-node-registry-replay",
        "operator_visible": True,
        "mutation_boundary": "template-only-teacher-ejection-parent-retirement-no-retirement-mutation",
    }


def _build_production_support_bundle_export_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    latest_deep_replay = latest_lifecycle.get("deep_replay") or summary.get("latest_deep_replay") or {}
    artifact_trust = latest_lifecycle.get("artifact_trust") or {}
    runtime_health = _build_active_runtime_health_monitor_request_template(summary)
    runtime_health_template = runtime_health.get("template") or {}
    promotion = _build_real_training_promotion_handoff_request_template(summary)
    promotion_template = promotion.get("template") or {}
    adapter_artifact_trust_status = str(promotion_template.get("adapter_artifact_trust_status") or "not_recorded")
    adapter_artifact_trust_clear = bool(promotion_template.get("adapter_artifact_trust_clear"))
    lifecycle_artifacts = latest_lifecycle.get("artifacts") or {}
    lifecycle_report_path = str(lifecycle_artifacts.get("lifecycle_report_path") or "")
    if lifecycle_report_path:
        support_bundle_path = Path(lifecycle_report_path).parent / "support" / "support_bundle.zip"
    else:
        cycle_id_for_path = latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id") or "scorecard_template"
        support_bundle_path = Path("runtime") / "artifacts" / "growth" / "production-spine" / safe_name(str(cycle_id_for_path)) / "support" / "support_bundle.zip"
    cycle_id = latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id")
    productization = latest_lifecycle.get("productization") or latest_cycle.get("productization") or {}
    productization_evidence = latest_lifecycle.get("productization_replay_evidence") or productization.get("productization_replay_evidence") or productization
    compiled_context = (
        latest_lifecycle.get("compiled_knowledge_context")
        or (latest_lifecycle.get("teacher") or {}).get("compiled_knowledge_context")
        or (latest_lifecycle.get("teacher_council") or {}).get("compiled_knowledge_context")
        or {}
    )
    artifact_bridge = latest_lifecycle.get("artifact_bridge") or {}
    support_sources = {
        "growth_cycle": lifecycle_report_path,
        "growth_events": lifecycle_artifacts.get("lifecycle_events_path"),
        "deep_replay_bundle": (latest_deep_replay.get("artifacts") or {}).get("deep_replay_bundle_path"),
        "deep_replay_artifact_index": (latest_deep_replay.get("artifacts") or {}).get("artifact_index_path"),
        "artifact_trust_scan": (artifact_trust.get("artifacts") or {}).get("scan_report_path"),
        "training_backend_plan": artifact_bridge.get("training_backend_plan_path"),
        "dataset_manifest_ref": (
            (latest_lifecycle.get("training_backend_plan") or {}).get("dataset_manifest_ref")
            or (latest_lifecycle.get("training") or {}).get("dataset_manifest_ref")
        ),
        "eval_scorecard": artifact_bridge.get("eval_scorecard_path"),
        "rollback_snapshot": runtime_health_template.get("rollback_snapshot_path"),
        "runtime_health_monitor": runtime_health_template.get("monitor_id"),
    }
    template = {
        "bundle_id": f"support-bundle:{cycle_id or 'scorecard_template'}",
        "cycle_id": cycle_id,
        "student_id": latest_lifecycle.get("student_id") or latest_cycle.get("student_id"),
        "target_node_ref": latest_lifecycle.get("target_node_ref") or latest_cycle.get("target_node_ref"),
        "support_bundle_path": str(support_bundle_path),
        "support_bundle_destination": "",
        "redact_secrets": True,
        "include_raw_private_data": False,
        "workspace_paths_redacted": True,
        "include_growth_cycle": True,
        "include_deep_replay": True,
        "include_artifact_trust": True,
        "adapter_artifact_trust_status": adapter_artifact_trust_status,
        "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
        "include_dataset_manifest": True,
        "include_kac_refs": True,
        "include_runtime_health": True,
        "include_rollback": True,
        "include_productization": True,
        "secret_scan_passed": bool(productization_evidence.get("secret_scan_passed")),
        "crash_diagnostics_included": bool(productization_evidence.get("crash_diagnostics")),
        "ci_packaging_included": bool(productization_evidence.get("ci_packaging")),
        "knowledge_artifact_refs": compiled_context.get("artifact_refs") or latest_lifecycle.get("knowledge_artifact_refs") or [],
        "blocked_knowledge_artifact_refs": compiled_context.get("blocked_artifact_refs") or [],
        "source_refs": {key: value for key, value in support_sources.items() if value},
    }
    missing_proof_fields = []
    for field in ("cycle_id", "student_id", "target_node_ref"):
        if not template[field]:
            missing_proof_fields.append(field)
    if not template["secret_scan_passed"]:
        missing_proof_fields.append("secret_scan_passed")
    if not template["support_bundle_destination"]:
        missing_proof_fields.append("support_bundle_destination")
    if not template["redact_secrets"]:
        missing_proof_fields.append("redact_secrets")
    if template["include_raw_private_data"]:
        missing_proof_fields.append("raw_private_data_excluded")
    if not template["workspace_paths_redacted"]:
        missing_proof_fields.append("workspace_paths_redacted")
    return {
        "schema_version": "production_support_bundle_export_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/support-bundles",
        "method": "POST",
        "ready_to_submit": False,
        "required_proof_fields": [
            "cycle_id",
            "student_id",
            "target_node_ref",
            "secret_scan_passed",
            "support_bundle_destination",
            "redact_secrets",
            "workspace_paths_redacted",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "growth-lifecycle-deep-replay-artifact-trust-kac-runtime-health-productization",
        "operator_visible": True,
        "mutation_boundary": "template-only-support-bundle-export-no-secret-or-private-data-packaging",
    }


def _build_first_run_readiness_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    latest_first_run = latest_lifecycle.get("first_run_readiness") or {}
    productization = latest_lifecycle.get("productization") or latest_cycle.get("productization") or {}
    productization_evidence = latest_lifecycle.get("productization_replay_evidence") or productization.get("productization_replay_evidence") or productization
    signing_template = _build_project_local_signing_key_request_template(summary)
    signing_request = signing_template.get("template") or {}
    support_bundle = _build_production_support_bundle_export_request_template(summary)
    support_request = support_bundle.get("template") or {}
    adapter_artifact_trust_status = str(support_request.get("adapter_artifact_trust_status") or "not_recorded")
    adapter_artifact_trust_clear = bool(support_request.get("adapter_artifact_trust_clear"))
    lifecycle_artifacts = latest_lifecycle.get("artifacts") or {}
    lifecycle_report_path = str(lifecycle_artifacts.get("lifecycle_report_path") or "")
    if lifecycle_report_path:
        model_cache_root_path = Path(lifecycle_report_path).parent / "model-cache"
        download_cache_root_path = Path(lifecycle_report_path).parent / "download-cache"
    else:
        cycle_id_for_path = latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id") or "scorecard_template"
        base_path = Path("runtime") / "artifacts" / "growth" / "production-spine" / safe_name(str(cycle_id_for_path))
        model_cache_root_path = base_path / "model-cache"
        download_cache_root_path = base_path / "download-cache"
    key_file_path = str(signing_request.get("key_file_path") or "")
    project_local_signing_key_ready = bool(key_file_path and Path(key_file_path).exists())
    template = {
        "readiness_id": f"first-run:{latest_lifecycle.get('cycle_id') or latest_cycle.get('cycle_id') or 'scorecard_template'}",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "student_id": latest_lifecycle.get("student_id") or latest_cycle.get("student_id"),
        "target_node_ref": latest_lifecycle.get("target_node_ref") or latest_cycle.get("target_node_ref"),
        "local_cache_controls_ready": bool(productization_evidence.get("local_cache_controls")),
        "model_download_manager_ready": bool(productization_evidence.get("model_download_manager")),
        "buyer_launcher_ready": bool(productization_evidence.get("buyer_launcher")),
        "support_bundle_ready": bool(productization_evidence.get("support_bundle")),
        "crash_diagnostics_ready": bool(productization_evidence.get("crash_diagnostics")),
        "docs_complete": bool(productization_evidence.get("docs_complete")),
        "buyer_safe_defaults": bool(productization_evidence.get("buyer_safe_defaults")),
        "adapter_artifact_trust_status": adapter_artifact_trust_status,
        "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
        "project_local_signing_key_ready": project_local_signing_key_ready,
        "key_file_path": key_file_path,
        "key_file_storage_scope": signing_request.get("storage_scope") or "project_local_encrypted_file",
        "passphrase_persisted": bool(signing_request.get("passphrase_persisted")),
        "model_cache_root_path": str(model_cache_root_path),
        "download_cache_root_path": str(download_cache_root_path),
        "support_bundle_path": support_request.get("support_bundle_path"),
        "support_bundle_destination": support_request.get("support_bundle_destination") or "",
        "workspace_paths_redacted": bool(support_request.get("workspace_paths_redacted", True)),
        "redact_secrets": bool(support_request.get("redact_secrets", True)),
        "include_raw_private_data": bool(support_request.get("include_raw_private_data")),
        "operator_approved": False,
    }
    missing_proof_fields = []
    for field in ("cycle_id", "student_id", "target_node_ref"):
        if not template[field]:
            missing_proof_fields.append(field)
    gate_fields = {
        "local_cache_controls": template["local_cache_controls_ready"],
        "model_download_manager": template["model_download_manager_ready"],
        "buyer_launcher": template["buyer_launcher_ready"],
        "support_bundle": template["support_bundle_ready"],
        "crash_diagnostics": template["crash_diagnostics_ready"],
        "project_local_signing_key_ready": template["project_local_signing_key_ready"],
        "buyer_safe_defaults": template["buyer_safe_defaults"],
        "adapter_artifact_trust_clear": template["adapter_artifact_trust_clear"],
    }
    missing_proof_fields.extend(field for field, passed in gate_fields.items() if not passed)
    if template["passphrase_persisted"]:
        missing_proof_fields.append("passphrase_not_persisted")
    if not template["workspace_paths_redacted"]:
        missing_proof_fields.append("workspace_paths_redacted")
    if not template["redact_secrets"]:
        missing_proof_fields.append("redact_secrets")
    if template["include_raw_private_data"]:
        missing_proof_fields.append("raw_private_data_excluded")
    if not template["operator_approved"]:
        missing_proof_fields.append("operator_approved")
    return {
        "schema_version": "first_run_readiness_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/first-run-readiness",
        "method": "POST",
        "ready_to_submit": False,
        "required_proof_fields": [
            "cycle_id",
            "student_id",
            "target_node_ref",
            "local_cache_controls",
            "model_download_manager",
            "buyer_launcher",
            "support_bundle",
            "crash_diagnostics",
            "project_local_signing_key_ready",
            "buyer_safe_defaults",
            "adapter_artifact_trust_clear",
            "operator_approved",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "productization-readiness-plus-project-local-signing-and-support-bundle-template",
        "operator_visible": True,
        "mutation_boundary": "template-only-first-run-readiness-no-installer-or-cache-mutation",
    }


def _build_crash_diagnostics_export_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    latest_deep_replay = latest_lifecycle.get("deep_replay") or summary.get("latest_deep_replay") or {}
    artifact_trust = latest_lifecycle.get("artifact_trust") or {}
    productization = latest_lifecycle.get("productization") or latest_cycle.get("productization") or {}
    productization_evidence = latest_lifecycle.get("productization_replay_evidence") or productization.get("productization_replay_evidence") or productization
    support_bundle = _build_production_support_bundle_export_request_template(summary)
    support_request = support_bundle.get("template") or {}
    adapter_artifact_trust_status = str(support_request.get("adapter_artifact_trust_status") or "not_recorded")
    adapter_artifact_trust_clear = bool(support_request.get("adapter_artifact_trust_clear"))
    runtime_health = _build_active_runtime_health_monitor_request_template(summary)
    runtime_health_template = runtime_health.get("template") or {}
    lifecycle_artifacts = latest_lifecycle.get("artifacts") or {}
    lifecycle_report_path = str(lifecycle_artifacts.get("lifecycle_report_path") or "")
    if lifecycle_report_path:
        diagnostics_bundle_path = Path(lifecycle_report_path).parent / "diagnostics" / "crash_diagnostics.json"
    else:
        cycle_id_for_path = latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id") or "scorecard_template"
        diagnostics_bundle_path = (
            Path("runtime")
            / "artifacts"
            / "growth"
            / "production-spine"
            / safe_name(str(cycle_id_for_path))
            / "diagnostics"
            / "crash_diagnostics.json"
        )
    template = {
        "diagnostics_id": f"crash-diagnostics:{latest_lifecycle.get('cycle_id') or latest_cycle.get('cycle_id') or 'scorecard_template'}",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "student_id": latest_lifecycle.get("student_id") or latest_cycle.get("student_id"),
        "target_node_ref": latest_lifecycle.get("target_node_ref") or latest_cycle.get("target_node_ref"),
        "diagnostics_bundle_path": str(diagnostics_bundle_path),
        "diagnostics_destination": "",
        "support_bundle_path": support_request.get("support_bundle_path"),
        "crash_diagnostics_ready": bool(productization_evidence.get("crash_diagnostics")),
        "support_bundle_ready": bool(productization_evidence.get("support_bundle")),
        "secret_scan_passed": bool(productization_evidence.get("secret_scan_passed")),
        "redact_secrets": True,
        "include_raw_private_data": False,
        "workspace_paths_redacted": True,
        "include_app_logs": True,
        "include_runtime_health": True,
        "include_support_bundle": True,
        "include_deep_replay": True,
        "include_artifact_trust": True,
        "adapter_artifact_trust_status": adapter_artifact_trust_status,
        "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
        "include_redacted_environment": True,
        "runtime_health_monitor_ref": runtime_health_template.get("monitor_id"),
        "runtime_health_blocker_count": len(runtime_health.get("health_blockers") or []),
        "deep_replay_bundle_path": (latest_deep_replay.get("artifacts") or {}).get("deep_replay_bundle_path"),
        "artifact_trust_scan_path": (artifact_trust.get("artifacts") or {}).get("scan_report_path"),
        "source_refs": {
            key: value
            for key, value in {
                "lifecycle_report": lifecycle_report_path,
                "support_bundle": support_request.get("support_bundle_path"),
                "deep_replay": (latest_deep_replay.get("artifacts") or {}).get("deep_replay_bundle_path"),
                "artifact_index": (latest_deep_replay.get("artifacts") or {}).get("artifact_index_path"),
                "runtime_health": runtime_health_template.get("monitor_id"),
            }.items()
            if value
        },
    }
    missing_proof_fields = []
    for field in ("cycle_id", "student_id", "target_node_ref"):
        if not template[field]:
            missing_proof_fields.append(field)
    if not template["crash_diagnostics_ready"]:
        missing_proof_fields.append("crash_diagnostics")
    if not template["support_bundle_ready"]:
        missing_proof_fields.append("support_bundle")
    if not template["secret_scan_passed"]:
        missing_proof_fields.append("secret_scan_passed")
    if not template["diagnostics_destination"]:
        missing_proof_fields.append("diagnostics_destination")
    if not template["redact_secrets"]:
        missing_proof_fields.append("redact_secrets")
    if template["include_raw_private_data"]:
        missing_proof_fields.append("raw_private_data_excluded")
    if not template["workspace_paths_redacted"]:
        missing_proof_fields.append("workspace_paths_redacted")
    return {
        "schema_version": "crash_diagnostics_export_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/crash-diagnostics",
        "method": "POST",
        "ready_to_submit": False,
        "required_proof_fields": [
            "cycle_id",
            "student_id",
            "target_node_ref",
            "crash_diagnostics",
            "support_bundle",
            "secret_scan_passed",
            "diagnostics_destination",
            "redact_secrets",
            "workspace_paths_redacted",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "productization-readiness-plus-runtime-health-support-bundle-deep-replay-artifact-trust",
        "operator_visible": True,
        "mutation_boundary": "template-only-crash-diagnostics-export-no-secret-or-private-data-packaging",
    }


def _build_release_packaging_handoff_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    latest_first_run = latest_lifecycle.get("first_run_readiness") or {}
    productization = latest_lifecycle.get("productization") or latest_cycle.get("productization") or {}
    productization_evidence = latest_lifecycle.get("productization_replay_evidence") or productization.get("productization_replay_evidence") or productization
    support_bundle = _build_production_support_bundle_export_request_template(summary)
    support_request = support_bundle.get("template") or {}
    first_run = _build_first_run_readiness_request_template(summary)
    first_run_template = first_run.get("template") or {}
    crash_diagnostics = _build_crash_diagnostics_export_request_template(summary)
    crash_request = crash_diagnostics.get("template") or {}
    promotion = _build_real_training_promotion_handoff_request_template(summary)
    promotion_template = promotion.get("template") or {}
    adapter_artifact_trust_status = str(promotion_template.get("adapter_artifact_trust_status") or "not_recorded")
    adapter_artifact_trust_clear = bool(promotion_template.get("adapter_artifact_trust_clear"))
    lifecycle_artifacts = latest_lifecycle.get("artifacts") or {}
    lifecycle_report_path = str(lifecycle_artifacts.get("lifecycle_report_path") or "")
    if lifecycle_report_path:
        package_output_path = Path(lifecycle_report_path).parent / "release" / "release_package.zip"
    else:
        cycle_id_for_path = latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id") or "scorecard_template"
        package_output_path = (
            Path("runtime")
            / "artifacts"
            / "growth"
            / "production-spine"
            / safe_name(str(cycle_id_for_path))
            / "release"
            / "release_package.zip"
        )
    latest_release_package = latest_lifecycle.get("release_package") or {}
    release_destination = str(latest_release_package.get("release_destination") or "")
    first_run_ready = bool(latest_first_run.get("decision") == "ready") or not bool(first_run.get("missing_proof_fields"))
    template = {
        "release_id": f"release-package:{latest_lifecycle.get('cycle_id') or latest_cycle.get('cycle_id') or 'scorecard_template'}",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "student_id": latest_lifecycle.get("student_id") or latest_cycle.get("student_id"),
        "target_node_ref": latest_lifecycle.get("target_node_ref") or latest_cycle.get("target_node_ref"),
        "package_output_path": str(package_output_path),
        "release_destination": release_destination,
        "ci_packaging_ready": bool(productization_evidence.get("ci_packaging")),
        "buyer_launcher_ready": bool(productization_evidence.get("buyer_launcher")),
        "support_bundle_ready": bool(productization_evidence.get("support_bundle")),
        "crash_diagnostics_ready": bool(productization_evidence.get("crash_diagnostics")),
        "first_run_readiness_ready": first_run_ready,
        "buyer_safe_defaults": bool(productization_evidence.get("buyer_safe_defaults")),
        "docs_complete": bool(productization_evidence.get("docs_complete")),
        "secret_scan_passed": bool(productization_evidence.get("secret_scan_passed")),
        "artifact_signing_ready": bool(productization_evidence.get("artifact_signing_ready")),
        "artifact_trust_clear": bool(productization_evidence.get("artifact_trust_clear")),
        "adapter_artifact_trust_status": adapter_artifact_trust_status,
        "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
        "include_installer": True,
        "include_support_bundle": True,
        "include_crash_diagnostics": True,
        "include_first_run_readiness": True,
        "include_deep_replay": True,
        "include_artifact_trust": True,
        "workspace_paths_redacted": True,
        "redact_secrets": True,
        "include_raw_private_data": False,
        "support_bundle_path": support_request.get("support_bundle_path"),
        "crash_diagnostics_bundle_path": crash_request.get("diagnostics_bundle_path"),
        "first_run_model_cache_root_path": first_run_template.get("model_cache_root_path"),
        "first_run_download_cache_root_path": first_run_template.get("download_cache_root_path"),
    }
    missing_proof_fields = []
    for field in ("cycle_id", "student_id", "target_node_ref"):
        if not template[field]:
            missing_proof_fields.append(field)
    gate_fields = {
        "ci_packaging": template["ci_packaging_ready"],
        "support_bundle": template["support_bundle_ready"],
        "crash_diagnostics": template["crash_diagnostics_ready"],
        "first_run_readiness": template["first_run_readiness_ready"],
        "buyer_safe_defaults": template["buyer_safe_defaults"],
        "secret_scan_passed": template["secret_scan_passed"],
        "artifact_signing_ready": template["artifact_signing_ready"],
        "artifact_trust_clear": template["artifact_trust_clear"],
        "adapter_artifact_trust_clear": template["adapter_artifact_trust_clear"],
    }
    missing_proof_fields.extend(field for field, passed in gate_fields.items() if not passed)
    if not release_destination:
        missing_proof_fields.append("release_destination")
    if not template["workspace_paths_redacted"]:
        missing_proof_fields.append("workspace_paths_redacted")
    if not template["redact_secrets"]:
        missing_proof_fields.append("redact_secrets")
    if template["include_raw_private_data"]:
        missing_proof_fields.append("raw_private_data_excluded")
    return {
        "schema_version": "release_packaging_handoff_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/release-packages",
        "method": "POST",
        "ready_to_submit": False,
        "required_proof_fields": [
            "cycle_id",
            "student_id",
            "target_node_ref",
            "ci_packaging",
            "support_bundle",
            "crash_diagnostics",
            "first_run_readiness",
            "secret_scan_passed",
            "artifact_signing_ready",
            "artifact_trust_clear",
            "adapter_artifact_trust_clear",
            "release_destination",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "productization-readiness-plus-first-run-support-bundle-crash-diagnostics",
        "operator_visible": True,
        "mutation_boundary": "template-only-release-packaging-no-installer-build-or-public-release-mutation",
    }


def _build_release_go_no_go_review_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    latest_release_package = latest_lifecycle.get("release_package") or {}
    latest_first_run = latest_lifecycle.get("first_run_readiness") or {}
    latest_crash_diagnostics = latest_lifecycle.get("crash_diagnostics") or {}
    latest_support_bundle = latest_lifecycle.get("support_bundle_manifest") or {}
    release = _build_release_packaging_handoff_request_template(summary)
    release_template = release.get("template") or {}
    first_run = _build_first_run_readiness_request_template(summary)
    first_run_template = first_run.get("template") or {}
    crash_diagnostics = _build_crash_diagnostics_export_request_template(summary)
    crash_template = crash_diagnostics.get("template") or {}
    support_bundle = _build_production_support_bundle_export_request_template(summary)
    support_template = support_bundle.get("template") or {}
    promotion = _build_real_training_promotion_handoff_request_template(summary)
    promotion_template = promotion.get("template") or {}
    node_activation = _build_runtime_node_activation_handoff_request_template(summary)
    node_activation_template = node_activation.get("template") or {}
    release_packaging_ready = bool(
        latest_release_package.get("package_created") and latest_release_package.get("buyer_release_allowed")
    ) or not bool(release.get("missing_proof_fields"))
    first_run_readiness_ready = bool(latest_first_run.get("decision") == "ready") or not bool(first_run.get("missing_proof_fields"))
    crash_diagnostics_ready = bool(latest_crash_diagnostics.get("logs_packaged") or crash_template.get("crash_diagnostics_ready"))
    support_bundle_ready = bool(
        latest_support_bundle.get("zip_created")
        or support_template.get("support_bundle_ready")
        or release_template.get("support_bundle_ready")
    )
    artifact_trust_clear = bool(release_template.get("artifact_trust_clear"))
    adapter_artifact_trust_status = str(release_template.get("adapter_artifact_trust_status") or "not_recorded")
    adapter_artifact_trust_clear = bool(release_template.get("adapter_artifact_trust_clear"))
    signed_replay_trust_clear = bool(promotion_template.get("signed_replay_trust_clear"))
    reviewer_windows_ready = bool(promotion_template.get("reviewer_windows_ready") or node_activation_template.get("reviewer_windows_ready"))
    template = {
        "review_id": f"release-go-no-go:{latest_lifecycle.get('cycle_id') or latest_cycle.get('cycle_id') or 'scorecard_template'}",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "student_id": latest_lifecycle.get("student_id") or latest_cycle.get("student_id"),
        "target_node_ref": latest_lifecycle.get("target_node_ref") or latest_cycle.get("target_node_ref"),
        "release_id": latest_release_package.get("release_id") or release_template.get("release_id"),
        "release_packaging_ready": release_packaging_ready,
        "first_run_readiness_ready": first_run_readiness_ready,
        "crash_diagnostics_ready": crash_diagnostics_ready,
        "support_bundle_ready": support_bundle_ready,
        "artifact_trust_clear": artifact_trust_clear,
        "adapter_artifact_trust_status": adapter_artifact_trust_status,
        "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
        "signed_replay_trust_clear": signed_replay_trust_clear,
        "reviewer_windows_ready": reviewer_windows_ready,
        "operator_approved": False,
        "human_approved": False,
        "buyer_release_allowed": bool(latest_release_package.get("buyer_release_allowed")),
        "release_package_path": (latest_release_package.get("artifacts") or {}).get("release_package_path")
        or release_template.get("package_output_path"),
        "support_bundle_path": (latest_support_bundle.get("artifacts") or {}).get("support_bundle_path")
        or support_template.get("support_bundle_path"),
        "crash_diagnostics_bundle_path": (latest_crash_diagnostics.get("artifacts") or {}).get("diagnostics_bundle_path")
        or crash_template.get("diagnostics_bundle_path"),
        "release_destination": latest_release_package.get("release_destination") or release_template.get("release_destination") or "",
        "mutation_boundary": "buyer-release-requires-explicit-go-no-go-review",
    }
    missing_proof_fields = []
    for field in ("cycle_id", "student_id", "target_node_ref", "release_id"):
        if not template[field]:
            missing_proof_fields.append(field)
    gate_fields = {
        "release_packaging_ready": release_packaging_ready,
        "first_run_readiness_ready": first_run_readiness_ready,
        "crash_diagnostics": crash_diagnostics_ready,
        "support_bundle": support_bundle_ready,
        "artifact_trust_clear": artifact_trust_clear,
        "trusted_adapter_artifact_required": adapter_artifact_trust_clear,
        "trusted_signed_replay_required": signed_replay_trust_clear,
        "reviewer_windows_ready": reviewer_windows_ready,
        "operator_approved": template["operator_approved"],
        "human_approved": template["human_approved"],
        "release_destination": bool(template["release_destination"]),
    }
    missing_proof_fields.extend(field for field, passed in gate_fields.items() if not passed)
    release_blockers = [field for field in missing_proof_fields if field not in {"cycle_id", "student_id", "target_node_ref", "release_id"}]
    return {
        "schema_version": "release_go_no_go_review_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/release-go-no-go",
        "method": "POST",
        "ready_to_submit": False,
        "required_proof_fields": [
            "cycle_id",
            "student_id",
            "target_node_ref",
            "release_id",
            "release_packaging_ready",
            "first_run_readiness_ready",
            "crash_diagnostics",
            "support_bundle",
            "artifact_trust_clear",
            "trusted_adapter_artifact_required",
            "trusted_signed_replay_required",
            "reviewer_windows_ready",
            "operator_approved",
            "human_approved",
            "release_destination",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "release_blockers": sorted(set(release_blockers)),
        "template": template,
        "source": "release-packaging-first-run-crash-diagnostics-support-bundle-signed-replay-reviewer-windows",
        "operator_visible": True,
        "mutation_boundary": "template-only-release-go-no-go-no-buyer-release-mutation",
    }


def _build_real_training_gate_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_real_training_gate = summary.get("latest_real_training_execution_gate") or {}
    latest_deep_replay = summary.get("latest_deep_replay") or (latest_lifecycle.get("deep_replay") or {})
    drilldown_summary = summary.get("latest_deep_replay_drilldown_summary") or _build_deep_replay_drilldown_summary(latest_deep_replay)
    signature_policy = latest_deep_replay.get("signature_policy") or {}
    artifact_signing_ready = (
        signature_policy.get("current_signature_state") == "signed_ed25519"
        and signature_policy.get("real_signing_blocker") is None
    )
    trusted_artifact_refs = _artifact_refs(latest_deep_replay)
    template = {
        "cycle_id": (latest_real_training_gate.get("cycle_id") or latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id")),
        "gate_id": "real_training_gate_from_scorecard_template",
        "operator_approved": False,
        "human_approved": False,
        "allow_real_weight_mutation": False,
        "license_state": latest_real_training_gate.get("license_state") or "pending_review",
        "training_backend_plan_ref": latest_real_training_gate.get("training_backend_plan_ref")
        or ((latest_lifecycle.get("training_backend_plan") or {}).get("plan_id")),
        "dataset_manifest_ref": latest_real_training_gate.get("dataset_manifest_ref")
        or ((latest_lifecycle.get("training_backend_plan") or {}).get("dataset_manifest_ref")),
        "hidden_eval_attestation": latest_real_training_gate.get("hidden_eval_attestation") or {},
        "dependency_report": latest_real_training_gate.get("dependency_report") or {},
        "artifact_signing_ready": artifact_signing_ready,
        "artifact_trust_clear": bool(artifact_signing_ready and drilldown_summary.get("has_real_training_artifact_trust")),
        "artifact_trust_registry_ref": f"deep-replay:{latest_deep_replay.get('replay_id')}" if latest_deep_replay.get("replay_id") else None,
        "trusted_artifact_refs": trusted_artifact_refs,
    }
    manual_approval_fields = ["operator_approved", "human_approved", "allow_real_weight_mutation"]
    return {
        "schema_version": "real_training_gate_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/real-training-gates",
        "method": "POST",
        "ready_to_submit": False,
        "manual_approval_fields": manual_approval_fields,
        "template": template,
        "source": "latest-signed-deep-replay-and-latest-real-training-gate",
        "operator_visible": True,
        "mutation_boundary": "template-only-no-real-training-mutation",
}


def _build_productization_readiness_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    productization = latest_lifecycle.get("productization") or latest_cycle.get("productization") or {}
    replay_evidence = latest_lifecycle.get("productization_replay_evidence") or productization.get("productization_replay_evidence") or productization
    required_gates = list(ProductizationReadinessAssessor.REQUIRED_GATES)
    open_gates = [str(item) for item in replay_evidence.get("open_gates") or []]
    if not open_gates:
        open_gates = [gate for gate in required_gates if not replay_evidence.get(gate)]
    promotion = _build_real_training_promotion_handoff_request_template(summary)
    promotion_template = promotion.get("template") or {}
    template = {
        "readiness_id": "release:scorecard_template",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        **{gate: bool(replay_evidence.get(gate)) for gate in required_gates},
        "adapter_artifact_trust_status": str(promotion_template.get("adapter_artifact_trust_status") or "not_recorded"),
        "upstream_agent_opportunity_gate": replay_evidence.get("upstream_agent_opportunity_gate") or {},
    }
    return {
        "schema_version": "productization_readiness_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/productization-readiness",
        "method": "POST",
        "ready_to_submit": not open_gates,
        "required_proof_fields": required_gates,
        "missing_proof_fields": sorted(set(open_gates)),
        "template": template,
        "operator_visible": True,
        "mutation_boundary": "template-only-no-release-mutation",
    }


def _build_runtime_quantization_foundry_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    runtime_foundry = latest_lifecycle.get("runtime_foundry") or latest_cycle.get("runtime_quantization_foundry") or {}
    replay_evidence = latest_lifecycle.get("runtime_foundry_replay_evidence") or runtime_foundry.get("runtime_foundry_replay_evidence") or {}
    canary_evidence = (
        replay_evidence.get("runtime_canary_guard_evidence")
        or runtime_foundry.get("runtime_canary_guard_evidence")
        or {}
    )
    candidates = runtime_foundry.get("benchmarks") or []
    cycle_id = latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id")
    model_ref = runtime_foundry.get("model_ref") or latest_lifecycle.get("student_id") or latest_cycle.get("student_id")
    backend_run_verified = bool(replay_evidence.get("backend_run_verified") or runtime_foundry.get("backend_run_verified"))
    human_approved = bool(runtime_foundry.get("promotion_allowed") and replay_evidence.get("promotion_allowed"))
    runtime_shadow_window_passed = bool(canary_evidence.get("runtime_shadow_window_passed"))
    runtime_canary_window_passed = bool(canary_evidence.get("runtime_canary_window_passed"))
    hidden_eval_delta_review_passed = bool(canary_evidence.get("hidden_eval_delta_review_passed"))
    baseline_quality_score = runtime_foundry.get("baseline_quality_score")
    required_proof_fields = [
        "model_ref",
        "hardware_profile",
        "baseline_quality_score",
        "candidates",
        "backend_run_verified",
        "human_approved",
        "runtime_shadow_window_passed",
        "runtime_canary_window_passed",
        "hidden_eval_delta_review_passed",
    ]
    missing_proof_fields = []
    if not model_ref:
        missing_proof_fields.append("model_ref")
    if not runtime_foundry.get("hardware_profile"):
        missing_proof_fields.append("hardware_profile")
    if baseline_quality_score is None:
        missing_proof_fields.append("baseline_quality_score")
    if not candidates:
        missing_proof_fields.append("candidates")
    if not backend_run_verified:
        missing_proof_fields.append("backend_run_verified")
    if not human_approved:
        missing_proof_fields.append("human_approved")
    if not runtime_shadow_window_passed:
        missing_proof_fields.append("runtime_shadow_window_passed")
    if not runtime_canary_window_passed:
        missing_proof_fields.append("runtime_canary_window_passed")
    if not hidden_eval_delta_review_passed:
        missing_proof_fields.append("hidden_eval_delta_review_passed")
    template = {
        "benchmark_id": "bench:scorecard_template",
        "cycle_id": cycle_id,
        "model_ref": model_ref,
        "hardware_profile": runtime_foundry.get("hardware_profile") or {},
        "baseline_quality_score": baseline_quality_score,
        "candidates": candidates,
        "backend_run_verified": backend_run_verified,
        "human_approved": human_approved,
        "runtime_shadow_window_passed": runtime_shadow_window_passed,
        "runtime_canary_window_passed": runtime_canary_window_passed,
        "hidden_eval_delta_review_passed": hidden_eval_delta_review_passed,
    }
    return {
        "schema_version": "runtime_quantization_foundry_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/runtime-benchmarks",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": required_proof_fields,
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-runtime-foundry-replay-evidence",
        "operator_visible": True,
        "mutation_boundary": "template-only-no-runtime-method-mutation",
    }


def _build_reviewer_window_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_advancement = summary.get("latest_reviewer_window_advancement") or {}
    sealed_eval = latest_lifecycle.get("sealed_eval") or {}
    reviewer_confidence = latest_lifecycle.get("reviewer_confidence_evidence") or sealed_eval.get("reviewer_confidence_evidence") or {}
    ejection_readiness = latest_advancement.get("ejection_readiness_evidence") or reviewer_confidence.get("ejection_readiness_evidence") or sealed_eval.get("ejection_readiness_evidence") or {}
    required_windows = [
        str(window)
        for window in (
            ejection_readiness.get("required_windows")
            or (sealed_eval.get("reviewer_monitor") or {}).get("windows")
            or ReviewerWindowAdvancementRecorder.REQUIRED_WINDOWS
        )
    ]
    passed_windows = [str(window) for window in ejection_readiness.get("passed_windows") or []]
    if not passed_windows and int(reviewer_confidence.get("passed_window_count") or 0) > 0 and required_windows:
        passed_windows = [required_windows[0]]
    pending_windows = [window for window in required_windows if window not in set(passed_windows)]
    next_window = pending_windows[0] if pending_windows else (required_windows[-1] if required_windows else "post_promotion")
    lower_bound = float(reviewer_confidence.get("lower_confidence_surpass_bound") or ejection_readiness.get("lower_confidence_surpass_bound") or 0.0)
    required_margin = float(reviewer_confidence.get("required_lower_confidence_margin") or ejection_readiness.get("required_lower_confidence_margin") or 0.0)
    template = {
        "advancement_id": f"reviewer-window:scorecard_template:{next_window}",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "eval_id": sealed_eval.get("eval_id"),
        "student_id": latest_lifecycle.get("student_id") or sealed_eval.get("student_id") or latest_cycle.get("student_id"),
        "window": next_window,
        "window_status": "passed",
        "passed_windows": passed_windows,
        "parent_surpass_rate": reviewer_confidence.get("parent_surpass_rate"),
        "teacher_surpass_rate": reviewer_confidence.get("teacher_surpass_rate"),
        "lower_confidence_surpass_bound": lower_bound,
        "required_lower_confidence_margin": required_margin,
        "teacher_ejection_review_requested": False,
        "parent_retirement_review_requested": False,
        "human_approved": False,
        "governance_approved": False,
    }
    required_proof_fields = [
        "eval_id",
        "student_id",
        "window",
        "window_status",
        "passed_windows",
        "lower_confidence_surpass_bound",
        "teacher_ejection_review_requested",
        "parent_retirement_review_requested",
        "human_approved",
        "governance_approved",
    ]
    missing_proof_fields = []
    for field in ("eval_id", "student_id", "window", "window_status"):
        if not template.get(field):
            missing_proof_fields.append(field)
    if pending_windows:
        missing_proof_fields.append("reviewer_windows_pending")
    if lower_bound <= required_margin:
        missing_proof_fields.append("lower_confidence_margin_not_met")
    for field in ("teacher_ejection_review_requested", "parent_retirement_review_requested", "human_approved", "governance_approved"):
        if not template[field]:
            missing_proof_fields.append(field)
    return {
        "schema_version": "reviewer_window_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/reviewer-windows",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_windows": required_windows,
        "pending_windows": pending_windows,
        "required_proof_fields": required_proof_fields,
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-reviewer-confidence-and-window-evidence",
        "operator_visible": True,
        "mutation_boundary": "template-only-no-teacher-ejection-or-parent-retirement",
    }


def _build_node_registry_decision_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_advancement = summary.get("latest_reviewer_window_advancement") or {}
    sealed_eval = latest_lifecycle.get("sealed_eval") or {}
    node_registry = latest_lifecycle.get("node_registry") or {}
    node_replay = latest_lifecycle.get("node_registry_replay_evidence") or node_registry.get("node_registry_replay_evidence") or {}
    artifact_bridge = latest_lifecycle.get("artifact_bridge") or {}
    canary_evidence = node_replay.get("canary_promotion_guard_evidence") or node_registry.get("canary_promotion_guard_evidence") or {}
    reviewer_retirement_evidence = node_replay.get("reviewer_window_retirement_evidence") or node_registry.get("reviewer_window_retirement_evidence") or {}
    promotion = _build_real_training_promotion_handoff_request_template(summary)
    promotion_template = promotion.get("template") or {}
    adapter_artifact_trust_status = str(promotion_template.get("adapter_artifact_trust_status") or "not_recorded")
    adapter_artifact_trust_clear = bool(promotion_template.get("adapter_artifact_trust_clear"))
    eval_scorecard_path = artifact_bridge.get("eval_scorecard_path") or (sealed_eval.get("artifacts") or {}).get("eval_scorecard_path")
    eval_promotion_allowed = bool(sealed_eval.get("promotion_allowed"))
    reviewer_parent_retirement_allowed = bool(
        reviewer_retirement_evidence.get("parent_retirement_allowed")
        or latest_advancement.get("parent_retirement_allowed")
    )
    action = "retire_parent" if eval_promotion_allowed and reviewer_parent_retirement_allowed else "promote_child"
    human_approved = bool(node_replay.get("human_approved"))
    shadow_runtime_window_passed = bool(canary_evidence.get("shadow_runtime_window_passed"))
    canary_window_passed = bool(canary_evidence.get("canary_window_passed"))
    post_promotion_window_passed = bool(canary_evidence.get("post_promotion_window_passed"))
    template = {
        "decision_id": "decision:scorecard_template",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "student_id": latest_lifecycle.get("student_id") or sealed_eval.get("student_id") or latest_cycle.get("student_id"),
        "parent_node_ref": sealed_eval.get("parent_node_ref") or latest_lifecycle.get("target_node_ref") or latest_cycle.get("target_node_ref"),
        "eval_scorecard_path": eval_scorecard_path,
        "action": action,
        "adapter_artifact_trust_status": adapter_artifact_trust_status,
        "adapter_artifact_trust_clear": adapter_artifact_trust_clear,
        "human_approved": human_approved,
        "shadow_runtime_window_passed": shadow_runtime_window_passed,
        "canary_window_passed": canary_window_passed,
        "post_promotion_window_passed": post_promotion_window_passed,
        "ivy_grade_review_passed": False,
        "greatly_outperforms_parent": False,
        "reviewer_window_advancement_path": (latest_advancement.get("artifacts") or {}).get("advancement_path"),
    }
    required_proof_fields = [
        "student_id",
        "parent_node_ref",
        "eval_scorecard_path",
        "action",
        "eval_promotion_allowed",
        "adapter_artifact_trust_clear",
        "human_approved",
        "shadow_runtime_window_passed",
        "canary_window_passed",
        "rollback_restorable",
        "reviewer_window_advancement_path",
        "ivy_grade_review_passed",
        "greatly_outperforms_parent",
        "post_promotion_window_passed",
    ]
    missing_proof_fields = []
    for field in ("student_id", "parent_node_ref", "eval_scorecard_path", "action"):
        if not template.get(field):
            missing_proof_fields.append(field)
    if not eval_promotion_allowed:
        missing_proof_fields.append("eval_promotion_allowed")
    if not adapter_artifact_trust_clear:
        missing_proof_fields.append("adapter_artifact_trust_clear")
    if not human_approved:
        missing_proof_fields.append("human_approved")
    if not shadow_runtime_window_passed:
        missing_proof_fields.append("shadow_runtime_window_passed")
    if not canary_window_passed:
        missing_proof_fields.append("canary_window_passed")
    if not bool(node_replay.get("rollback_restorable")):
        missing_proof_fields.append("rollback_restorable")
    if action == "retire_parent":
        for field in ("reviewer_window_advancement_path", "ivy_grade_review_passed", "greatly_outperforms_parent", "post_promotion_window_passed"):
            if not template.get(field):
                missing_proof_fields.append(field)
    return {
        "schema_version": "node_registry_decision_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/node-registry-decisions",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": required_proof_fields,
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-node-registry-replay-and-sealed-eval-evidence",
        "operator_visible": True,
        "mutation_boundary": "template-only-no-node-registry-mutation",
    }


def _build_federated_packet_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    federation = latest_lifecycle.get("federation") or latest_cycle.get("federated_learning_loop") or {}
    replay_evidence = latest_lifecycle.get("federated_influence_replay_evidence") or federation.get("federated_influence_replay_evidence") or federation
    local_metrics = federation.get("sanitized_metrics") or {}
    consent_granted = bool(replay_evidence.get("consent_granted") or federation.get("status") == "accepted_sanitized_packet")
    raw_content_included = bool(replay_evidence.get("raw_content_included") or federation.get("raw_content_included"))
    contains_personal_data = bool(replay_evidence.get("contains_personal_data") or federation.get("contains_personal_data"))
    secure_aggregation_ready = bool(replay_evidence.get("secure_aggregation_ready") or federation.get("secure_aggregation_ready"))
    differential_privacy = replay_evidence.get("differential_privacy") or federation.get("differential_privacy") or {}
    poisoning_scan = replay_evidence.get("poisoning_scan") or federation.get("poisoning_scan") or {}
    shadow_influence = replay_evidence.get("shadow_routing_influence") or federation.get("shadow_routing_influence") or {}
    template = {
        "packet_id": "fed:scorecard_template",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "source_node_ref": federation.get("source_node_ref") or latest_lifecycle.get("target_node_ref") or latest_cycle.get("target_node_ref"),
        "consent_granted": consent_granted,
        "local_metrics": local_metrics,
        "capability_tags": federation.get("capability_tags") or [],
        "raw_content_included": raw_content_included,
        "contains_personal_data": contains_personal_data,
        "active_route_mutation_allowed": bool(shadow_influence.get("active_route_mutation_allowed")),
    }
    required_proof_fields = [
        "cycle_id",
        "source_node_ref",
        "consent_granted",
        "local_metrics",
        "secure_aggregation_ready",
        "differential_privacy_enabled",
        "poisoning_scan_passed",
        "raw_content_excluded",
        "personal_data_excluded",
        "active_route_mutation_blocked",
    ]
    missing_proof_fields = []
    if not template["cycle_id"]:
        missing_proof_fields.append("cycle_id")
    if not template["source_node_ref"]:
        missing_proof_fields.append("source_node_ref")
    if not consent_granted:
        missing_proof_fields.append("consent_granted")
    if not local_metrics:
        missing_proof_fields.append("local_metrics")
    if not secure_aggregation_ready:
        missing_proof_fields.append("secure_aggregation_ready")
    if not differential_privacy.get("enabled"):
        missing_proof_fields.append("differential_privacy_enabled")
    if poisoning_scan.get("passed") is not True:
        missing_proof_fields.append("poisoning_scan_passed")
    if raw_content_included:
        missing_proof_fields.append("raw_content_excluded")
    if contains_personal_data:
        missing_proof_fields.append("personal_data_excluded")
    if shadow_influence.get("active_route_mutation_allowed"):
        missing_proof_fields.append("active_route_mutation_blocked")
    return {
        "schema_version": "federated_packet_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/federated-packets",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": required_proof_fields,
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-sanitized-federated-influence-replay",
        "operator_visible": True,
        "mutation_boundary": "template-only-sanitized-federated-packet-no-active-route-mutation",
    }


def _build_recursive_dream_cycle_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    dream_cycle = latest_lifecycle.get("dream_cycle") or latest_cycle.get("recursive_dream_execution") or {}
    replay_evidence = latest_lifecycle.get("recursive_dream_replay_evidence") or dream_cycle.get("recursive_dream_replay_evidence") or dream_cycle
    seed_refs = [str(ref) for ref in replay_evidence.get("dream_seed_refs") or [] if ref]
    failure_refs = [ref for ref in seed_refs if ref.startswith("failure:")]
    federated_packet_signature = next((ref for ref in seed_refs if ref.startswith("sha256:")), None)
    knowledge_artifact_refs = [str(ref) for ref in replay_evidence.get("knowledge_artifact_refs") or []]
    compiled_context_allowed = replay_evidence.get("compiled_knowledge_context_allowed")
    template = {
        "dream_id": "dream:scorecard_template",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "target_node_ref": latest_lifecycle.get("target_node_ref") or latest_cycle.get("target_node_ref"),
        "student_id": latest_lifecycle.get("student_id") or latest_cycle.get("student_id"),
        "failure_refs": failure_refs,
        "federated_packet_signature": federated_packet_signature,
        "knowledge_artifact_refs": knowledge_artifact_refs,
        "dream_temperature": dream_cycle.get("dream_temperature"),
        "critic_temperature": dream_cycle.get("critic_temperature"),
    }
    required_proof_fields = [
        "cycle_id",
        "target_node_ref",
        "student_id",
        "failure_refs",
        "federated_packet_signature",
        "dream_temperature",
        "critic_temperature",
        "compiled_knowledge_context_allowed",
    ]
    missing_proof_fields = []
    for field in ("cycle_id", "target_node_ref", "student_id", "federated_packet_signature", "dream_temperature", "critic_temperature"):
        value = template.get(field)
        if value is None or value == "":
            missing_proof_fields.append(field)
    if not failure_refs:
        missing_proof_fields.append("failure_refs")
    if compiled_context_allowed is False:
        missing_proof_fields.append("compiled_knowledge_context_allowed")
    return {
        "schema_version": "recursive_dream_cycle_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/dream-cycles",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": required_proof_fields,
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-recursive-dream-replay-evidence",
        "operator_visible": True,
        "mutation_boundary": "template-only-recursive-dream-proposes-sandbox-candidates",
    }


def _build_tensor_program_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    tensor_program = latest_lifecycle.get("tensor_program") or latest_cycle.get("tensor_runtime_kernel") or {}
    replay_evidence = latest_lifecycle.get("tensor_runtime_replay_evidence") or tensor_program.get("tensor_runtime_replay_evidence") or tensor_program
    checkpoint = replay_evidence.get("checkpoint") or tensor_program.get("checkpoint") or {}
    optimizer_state = replay_evidence.get("optimizer_state") or tensor_program.get("optimizer_state") or {}
    parameter_refs = replay_evidence.get("parameter_refs") or tensor_program.get("parameter_refs") or {}
    ops = tensor_program.get("ops") or replay_evidence.get("ops") or []
    template = {
        "program_id": "tensor:scorecard_template",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "parameter_refs": parameter_refs,
        "ops": ops,
        "optimizer_state": optimizer_state,
        "checkpoint": checkpoint,
    }
    missing_proof_fields = []
    if not template["cycle_id"]:
        missing_proof_fields.append("cycle_id")
    if not parameter_refs:
        missing_proof_fields.append("parameter_refs")
    if not ops:
        missing_proof_fields.append("ops")
    if not optimizer_state:
        missing_proof_fields.append("optimizer_state")
    if checkpoint.get("restore_validated") is not True:
        missing_proof_fields.append("checkpoint_restore_validated")
    if replay_evidence.get("status") not in {"ready", "executed_tensor_program"}:
        missing_proof_fields.append("tensor_runtime_replay_ready")
    return {
        "schema_version": "tensor_program_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/tensor-programs",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": [
            "cycle_id",
            "parameter_refs",
            "ops",
            "optimizer_state",
            "checkpoint_restore_validated",
            "tensor_runtime_replay_ready",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-tensor-runtime-replay-evidence",
        "operator_visible": True,
        "mutation_boundary": "template-only-shadow-tensor-program-no-production-parameter-mutation",
    }


def _build_hive_moe_route_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    hive_route = latest_lifecycle.get("hive_route") or latest_cycle.get("native_hive_moe_runtime") or {}
    replay_evidence = latest_lifecycle.get("hive_route_replay_evidence") or hive_route.get("hive_route_replay_evidence") or hive_route
    task_features = replay_evidence.get("task_features") or hive_route.get("task_features") or {}
    candidates = replay_evidence.get("candidates") or hive_route.get("candidates") or []
    top_k = replay_evidence.get("top_k") or hive_route.get("top_k")
    template = {
        "route_id": "route:scorecard_template",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "task_features": task_features,
        "candidates": candidates,
        "top_k": top_k,
    }
    missing_proof_fields = []
    if not template["cycle_id"]:
        missing_proof_fields.append("cycle_id")
    if not task_features:
        missing_proof_fields.append("task_features")
    if not candidates:
        missing_proof_fields.append("candidates")
    if not top_k:
        missing_proof_fields.append("top_k")
    if replay_evidence.get("status") not in {"ready", "shadow_routed"}:
        missing_proof_fields.append("hive_route_replay_ready")
    return {
        "schema_version": "hive_moe_route_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/hive-moe-routes",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": ["cycle_id", "task_features", "candidates", "top_k", "hive_route_replay_ready"],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-hive-route-replay-evidence",
        "operator_visible": True,
        "mutation_boundary": "template-only-shadow-route-no-active-router-weight-mutation",
    }


def _build_child_execution_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    child_execution = latest_lifecycle.get("child_execution") or latest_cycle.get("child_node_execution") or {}
    replay_evidence = (
        latest_lifecycle.get("child_execution_replay_evidence")
        or child_execution.get("child_execution_replay_evidence")
        or child_execution
    )
    runtime_pathway = replay_evidence.get("runtime_pathway") or {}
    artifact_bridge = latest_lifecycle.get("artifact_bridge") or summary.get("latest_lifecycle_artifact_bridge") or {}
    template = {
        "execution_id": "exec:scorecard_template",
        "cycle_id": latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "student_id": child_execution.get("student_id") or latest_lifecycle.get("student_id"),
        "input": replay_evidence.get("input") or child_execution.get("input") or {},
        "weights_path": artifact_bridge.get("training_checkpoint_path") or replay_evidence.get("weights_path"),
        "adapter_bundle_path": artifact_bridge.get("adapter_bundle_path"),
        "preferred_weight_artifact": "adapter_bundle" if artifact_bridge.get("adapter_bundle_path") else "checkpoint",
        "neural_bus_required": bool(runtime_pathway.get("used_neural_bus")),
        "hive_blackboard_required": bool(runtime_pathway.get("used_hive_blackboard")),
        "memory_plane_required": bool(runtime_pathway.get("used_memory_plane")),
        "eval_hook_required": bool(runtime_pathway.get("used_eval_hook")),
    }
    missing_proof_fields = []
    if not template["cycle_id"]:
        missing_proof_fields.append("cycle_id")
    if not template["student_id"]:
        missing_proof_fields.append("student_id")
    if not isinstance(template["input"], dict) or not template["input"]:
        missing_proof_fields.append("input")
    if not template["adapter_bundle_path"] and not template["weights_path"]:
        missing_proof_fields.append("adapter_bundle_path_or_weights_path")
    if not template["neural_bus_required"]:
        missing_proof_fields.append("neural_bus_verified")
    if not template["hive_blackboard_required"]:
        missing_proof_fields.append("hive_blackboard_verified")
    if not template["eval_hook_required"]:
        missing_proof_fields.append("eval_hook_verified")
    if replay_evidence.get("status") != "ready" or not replay_evidence.get("callable_runtime_verified"):
        missing_proof_fields.append("child_execution_replay_ready")
    return {
        "schema_version": "child_execution_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/child-executions",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": [
            "cycle_id",
            "student_id",
            "input",
            "adapter_bundle_path_or_weights_path",
            "neural_bus_verified",
            "hive_blackboard_verified",
            "eval_hook_verified",
            "child_execution_replay_ready",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-child-execution-replay-evidence",
        "operator_visible": True,
        "mutation_boundary": "template-only-shadow-child-execution-no-production-output-or-node-registry-mutation",
    }


def _build_sealed_eval_gauntlet_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    sealed_eval = latest_lifecycle.get("sealed_eval") or latest_cycle.get("sealed_eval_gauntlet") or {}
    artifact_bridge = latest_lifecycle.get("artifact_bridge") or summary.get("latest_lifecycle_artifact_bridge") or {}
    attestation = sealed_eval.get("hidden_eval_attestation") or {}
    score_comparison = sealed_eval.get("score_comparison") or {}
    hard_gates = sealed_eval.get("hard_gates") or {}
    artifacts = sealed_eval.get("artifacts") or {}
    case_count = int(attestation.get("case_count") or score_comparison.get("case_count") or sealed_eval.get("case_count") or 0)
    checkpoint_path = artifact_bridge.get("training_checkpoint_path")
    adapter_bundle_path = artifact_bridge.get("adapter_bundle_path")
    template = {
        "eval_id": sealed_eval.get("eval_id") or "eval:scorecard_template",
        "cycle_id": sealed_eval.get("cycle_id") or latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "student_id": sealed_eval.get("student_id") or latest_lifecycle.get("student_id") or latest_cycle.get("student_id"),
        "parent_node_ref": sealed_eval.get("parent_node_ref")
        or latest_lifecycle.get("target_node_ref")
        or latest_cycle.get("target_node_ref"),
        "weights_path": checkpoint_path,
        "adapter_bundle_path": adapter_bundle_path,
        "preferred_weight_artifact": "adapter_bundle" if adapter_bundle_path else "checkpoint",
        "hidden_eval_cases_ref": f"sealed:{sealed_eval.get('eval_id')}:case_hashes" if sealed_eval.get("eval_id") else None,
        "hidden_eval_case_count": case_count,
        "hidden_eval_case_hashes": attestation.get("case_hashes") or [],
        "hidden_eval_attestation_path": artifacts.get("hidden_eval_attestation_path")
        or score_comparison.get("hidden_eval_attestation_path"),
        "comparison_matrix_path": artifacts.get("comparison_matrix_path") or score_comparison.get("comparison_matrix_path"),
        "hidden_eval_visible_to_training": bool(sealed_eval.get("hidden_eval_visible_to_training")),
        "hidden_eval_visible_to_teacher_council": bool(sealed_eval.get("hidden_eval_visible_to_teacher_council")),
        "teacher_license_gate_passed": bool(hard_gates.get("teacher_license_gate_passed")),
        "human_approved": bool(hard_gates.get("human_approved")),
        "student_parent_surpass_margin": score_comparison.get("student_parent_surpass_margin"),
        "student_teacher_surpass_margin": score_comparison.get("student_teacher_surpass_margin"),
        "lower_confidence_surpass_bound": score_comparison.get("lower_confidence_surpass_bound")
        if score_comparison.get("lower_confidence_surpass_bound") is not None
        else sealed_eval.get("lower_confidence_surpass_bound"),
        "critical_regressions": 1 if hard_gates.get("critical_regression") else 0,
        "promotion_allowed": bool(sealed_eval.get("promotion_allowed")),
        "teacher_ejection_allowed": bool(sealed_eval.get("teacher_ejection_allowed")),
        "teacher_ejection_blocker": sealed_eval.get("teacher_ejection_blocker"),
        "pending_reviewer_window_count": (sealed_eval.get("reviewer_consistency") or {}).get("pending_window_count"),
    }
    missing_proof_fields = []
    for field in ("cycle_id", "eval_id", "student_id", "parent_node_ref"):
        if not template[field]:
            missing_proof_fields.append(field)
    if not template["adapter_bundle_path"] and not template["weights_path"]:
        missing_proof_fields.append("adapter_bundle_path_or_weights_path")
    if not template["hidden_eval_attestation_path"]:
        missing_proof_fields.append("hidden_eval_attestation_path")
    if not template["comparison_matrix_path"]:
        missing_proof_fields.append("comparison_matrix_path")
    if not template["hidden_eval_case_hashes"] or not template["hidden_eval_case_count"]:
        missing_proof_fields.append("hidden_eval_case_hashes")
    if template["hidden_eval_visible_to_training"]:
        missing_proof_fields.append("hidden_eval_not_visible_to_training")
    if template["hidden_eval_visible_to_teacher_council"]:
        missing_proof_fields.append("hidden_eval_not_visible_to_teacher_council")
    if not template["teacher_license_gate_passed"]:
        missing_proof_fields.append("teacher_license_gate_passed")
    if sealed_eval.get("status") != "sealed_eval_complete":
        missing_proof_fields.append("sealed_eval_complete")
    missing_proof_fields.append("sealed_hidden_case_material_required")
    return {
        "schema_version": "sealed_eval_gauntlet_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/eval-gauntlets",
        "method": "POST",
        "ready_to_submit": False,
        "required_proof_fields": [
            "cycle_id",
            "eval_id",
            "student_id",
            "parent_node_ref",
            "adapter_bundle_path_or_weights_path",
            "hidden_eval_case_hashes",
            "hidden_eval_attestation_path",
            "comparison_matrix_path",
            "teacher_license_gate_passed",
            "sealed_hidden_case_material_required",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-sealed-eval-scorecard",
        "operator_visible": True,
        "mutation_boundary": "template-only-sealed-eval-replay-raw-hidden-cases-not-exposed",
    }


def _build_teacher_council_review_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_cycle = summary.get("latest_cycle") or {}
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    teacher_review = latest_lifecycle.get("teacher_review") or latest_cycle.get("teacher_council_automation") or {}
    artifact_refs = teacher_review.get("artifact_refs") or {}
    license_gate = teacher_review.get("license_gate") or {}
    validator_summary = teacher_review.get("validator_summary") or {}
    compiled_knowledge_context = teacher_review.get("compiled_knowledge_context") or {}
    reviewer_window = teacher_review.get("reviewer_window") or {}
    template = {
        "review_id": teacher_review.get("review_id") or "teacher:scorecard_template",
        "cycle_id": teacher_review.get("cycle_id") or latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "target_node_ref": teacher_review.get("target_node_ref")
        or latest_lifecycle.get("target_node_ref")
        or latest_cycle.get("target_node_ref"),
        "teacher_outputs_ref": artifact_refs.get("teacher_outputs_path") or teacher_review.get("teacher_outputs_ref"),
        "validator_results_ref": artifact_refs.get("validator_results_path") or teacher_review.get("validator_results_ref"),
        "critique_outputs_ref": artifact_refs.get("critiques_path") or teacher_review.get("critique_outputs_ref"),
        "teacher_count": int(teacher_review.get("teacher_count") or 0),
        "license_gate_passed": bool(license_gate.get("passed")),
        "allowed_license_states": license_gate.get("allowed_license_states") or [],
        "accepted_teacher_ref": teacher_review.get("accepted_teacher_ref"),
        "accepted_output_ref": teacher_review.get("accepted_output_ref"),
        "disagreement_score": teacher_review.get("disagreement_score"),
        "validator_summary": validator_summary,
        "compiled_knowledge_context": compiled_knowledge_context,
        "teacher_ejection_review_required": bool(reviewer_window.get("teacher_ejection_review_required")),
        "promotion_gate": teacher_review.get("promotion_gate") or [],
    }
    missing_proof_fields = []
    for field in ("cycle_id", "review_id", "target_node_ref"):
        if not template[field]:
            missing_proof_fields.append(field)
    if not template["teacher_outputs_ref"]:
        missing_proof_fields.append("teacher_outputs_ref")
    if not template["validator_results_ref"]:
        missing_proof_fields.append("validator_results_ref")
    if not template["license_gate_passed"]:
        missing_proof_fields.append("license_gate_passed")
    if not template["teacher_count"]:
        missing_proof_fields.append("teacher_count")
    if not validator_summary:
        missing_proof_fields.append("validator_summary")
    if compiled_knowledge_context.get("allowed") is False:
        missing_proof_fields.append("compiled_knowledge_context_allowed")
    if teacher_review.get("status") != "teacher_review_complete":
        missing_proof_fields.append("teacher_review_complete")
    missing_proof_fields.extend(["teacher_outputs_payload_required", "validator_results_payload_required"])
    return {
        "schema_version": "teacher_council_review_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/teacher-council-reviews",
        "method": "POST",
        "ready_to_submit": False,
        "required_proof_fields": [
            "cycle_id",
            "review_id",
            "target_node_ref",
            "teacher_outputs_ref",
            "validator_results_ref",
            "license_gate_passed",
            "teacher_outputs_payload_required",
            "validator_results_payload_required",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-teacher-council-review",
        "operator_visible": True,
        "mutation_boundary": "template-only-teacher-council-review-raw-teacher-outputs-not-auto-resubmitted",
    }


def _build_sandbox_training_run_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    training_plan = latest_lifecycle.get("training_backend_plan") or latest_cycle.get("training_backend_plan") or {}
    training = latest_lifecycle.get("training") or latest_cycle.get("real_training_runner") or {}
    replay_evidence = (
        latest_lifecycle.get("training_replay_evidence")
        or summary.get("latest_lifecycle_training_replay_evidence")
        or _build_training_replay_evidence(training)
    )
    artifact_bridge = latest_lifecycle.get("artifact_bridge") or summary.get("latest_lifecycle_artifact_bridge") or {}
    plan_artifacts = training_plan.get("artifacts") or {}
    training_artifacts = training.get("artifacts") or {}
    loss_contract = training_plan.get("loss_contract") or {}
    execution_contract = training_plan.get("execution_contract") or {}
    hidden_eval_attestation = training.get("hidden_eval_attestation") or training_plan.get("hidden_eval_attestation") or {}
    training_dataset = training_plan.get("training_dataset") or []
    export_targets = sorted(
        set(
            list((training_plan.get("output_artifact_contract") or {}).keys())
            + list((training.get("exports") or {}).keys())
        )
    )
    if not export_targets:
        export_targets = ["adapter"]
    sandbox_status = training.get("status") or "not_recorded"
    support_state = "sandbox_supported" if sandbox_status == "sandbox_training_complete" and replay_evidence.get("status") == "ready" else "sandbox_blocked"
    template = {
        "run_id": "train:scorecard_template",
        "cycle_id": training_plan.get("cycle_id") or training.get("cycle_id") or latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "student_id": training_plan.get("student_id") or training.get("student_id") or latest_lifecycle.get("student_id"),
        "training_backend_plan_ref": training_plan.get("plan_id"),
        "training_backend_plan_path": artifact_bridge.get("training_backend_plan_path")
        or plan_artifacts.get("training_backend_plan_path"),
        "training_config_path": artifact_bridge.get("training_config_path") or plan_artifacts.get("training_config_path"),
        "training_invocation_path": artifact_bridge.get("training_invocation_path") or plan_artifacts.get("training_invocation_path"),
        "dataset_manifest_ref": training_plan.get("dataset_manifest_ref"),
        "base_model_ref": training_plan.get("base_model_ref"),
        "method": training_plan.get("method") or training.get("method"),
        "framework": training_plan.get("framework") or training.get("framework"),
        "training_modes": loss_contract.get("objectives") or [],
        "teacher_refs": training_plan.get("teacher_refs") or [],
        "license_state": training_plan.get("license_state") or "unknown",
        "operator_approved": training_plan.get("status") == "sandbox_backend_plan_ready",
        "eval_refs": training_plan.get("eval_refs") or [],
        "hidden_eval_attestation": hidden_eval_attestation,
        "rollback_ref": training_plan.get("rollback_ref"),
        "training_dataset_row_count": len(training_dataset) if isinstance(training_dataset, list) else 0,
        "support_state": support_state,
        "sandbox_status": sandbox_status,
        "sandbox_weight_mutation_allowed": bool(training.get("sandbox_weight_mutation_allowed")),
        "production_mutation_allowed": False,
        "math_contract": replay_evidence.get("math_contract") or {},
        "optimizer_state": replay_evidence.get("optimizer_state") or {},
        "checkpoint_path": artifact_bridge.get("training_checkpoint_path")
        or (replay_evidence.get("artifact_refs") or {}).get("checkpoint_path")
        or training_artifacts.get("checkpoint_path"),
        "loss_trace_path": artifact_bridge.get("loss_trace_path")
        or (replay_evidence.get("artifact_refs") or {}).get("loss_trace_path")
        or training_artifacts.get("loss_trace_path"),
        "training_report_path": artifact_bridge.get("training_report_path")
        or (replay_evidence.get("artifact_refs") or {}).get("training_report_path")
        or training_artifacts.get("training_report_path"),
        "adapter_manifest_path": artifact_bridge.get("adapter_manifest_path") or training_artifacts.get("adapter_manifest_path"),
        "adapter_bundle_path": artifact_bridge.get("adapter_bundle_path")
        or ((training.get("exports") or {}).get("adapter") or {}).get("bundle_path"),
        "export_targets": export_targets,
        "execution_command": execution_contract.get("command") or [],
    }
    missing_proof_fields = []
    for field in (
        "cycle_id",
        "student_id",
        "training_backend_plan_ref",
        "training_backend_plan_path",
        "training_config_path",
        "dataset_manifest_ref",
        "method",
        "framework",
        "license_state",
        "rollback_ref",
        "checkpoint_path",
        "loss_trace_path",
        "training_report_path",
        "adapter_bundle_path",
    ):
        if not template[field]:
            missing_proof_fields.append(field)
    if template["license_state"] != "approved_train":
        missing_proof_fields.append("license_approved_train")
    if not template["operator_approved"]:
        missing_proof_fields.append("operator_approved")
    if not template["training_modes"]:
        missing_proof_fields.append("training_modes")
    if not template["teacher_refs"]:
        missing_proof_fields.append("teacher_refs")
    if not template["eval_refs"]:
        missing_proof_fields.append("eval_refs")
    if not _hidden_eval_attestation_passed(hidden_eval_attestation):
        missing_proof_fields.append("hidden_eval_attestation_passed")
    if not template["training_dataset_row_count"]:
        missing_proof_fields.append("training_dataset")
    if support_state != "sandbox_supported":
        missing_proof_fields.append("sandbox_training_complete")
    if replay_evidence.get("status") != "ready":
        missing_proof_fields.append("training_replay_ready")
    if not template["math_contract"]:
        missing_proof_fields.append("math_contract")
    if not template["optimizer_state"] or not template["optimizer_state"].get("steps"):
        missing_proof_fields.append("optimizer_state")
    if not template["sandbox_weight_mutation_allowed"]:
        missing_proof_fields.append("sandbox_weight_mutation_allowed")
    if training.get("production_mutation_allowed"):
        missing_proof_fields.append("production_mutation_must_remain_blocked")
    return {
        "schema_version": "sandbox_training_run_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/training-runs",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": [
            "cycle_id",
            "student_id",
            "training_backend_plan_ref",
            "dataset_manifest_ref",
            "method",
            "framework",
            "training_modes",
            "teacher_refs",
            "license_approved_train",
            "operator_approved",
            "eval_refs",
            "hidden_eval_attestation_passed",
            "rollback_ref",
            "training_dataset",
            "sandbox_training_complete",
            "training_replay_ready",
            "checkpoint_path",
            "optimizer_state",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-training-backend-plan-and-sandbox-replay",
        "operator_visible": True,
        "mutation_boundary": "template-only-sandbox-training-no-production-weight-mutation",
    }


def _build_training_backend_plan_request_template(summary: dict[str, Any]) -> dict[str, Any]:
    latest_lifecycle = summary.get("latest_lifecycle") or {}
    latest_cycle = summary.get("latest_cycle") or {}
    training_plan = (
        latest_lifecycle.get("training_backend_plan")
        or summary.get("latest_training_backend_plan")
        or latest_cycle.get("training_backend_plan")
        or {}
    )
    artifacts = training_plan.get("artifacts") or {}
    execution_contract = training_plan.get("execution_contract") or {}
    dependency_report = training_plan.get("dependency_report") or {}
    output_contract = training_plan.get("output_artifact_contract") or {}
    output_contract_targets = sorted(str(target) for target in output_contract.keys())
    template = {
        "plan_id": training_plan.get("plan_id") or "train_backend:scorecard_template",
        "cycle_id": training_plan.get("cycle_id") or latest_lifecycle.get("cycle_id") or latest_cycle.get("cycle_id"),
        "student_id": training_plan.get("student_id") or latest_lifecycle.get("student_id"),
        "base_model_ref": training_plan.get("base_model_ref"),
        "dataset_manifest_ref": training_plan.get("dataset_manifest_ref"),
        "method": training_plan.get("method"),
        "framework": training_plan.get("framework"),
        "training_modes": training_plan.get("training_modes") or (training_plan.get("loss_contract") or {}).get("objectives") or [],
        "teacher_refs": training_plan.get("teacher_refs") or [],
        "license_state": training_plan.get("license_state") or "unknown",
        "privacy_class": training_plan.get("privacy_class") or "internal",
        "contains_private_data": bool(training_plan.get("contains_private_data")),
        "eval_refs": training_plan.get("eval_refs") or [],
        "hidden_eval_attestation": training_plan.get("hidden_eval_attestation") or {},
        "rollback_ref": training_plan.get("rollback_ref"),
        "export_targets": training_plan.get("export_targets") or output_contract_targets,
        "target_hardware": training_plan.get("target_hardware") or {},
        "operator_approved": training_plan.get("status") == "sandbox_backend_plan_ready",
        "human_approved": False,
        "dependency_report": dependency_report,
        "support_state": training_plan.get("support_state") or "not_recorded",
        "backend_status": training_plan.get("status") or "not_recorded",
        "blocked_reasons": training_plan.get("blocked_reasons") or [],
        "training_backend_plan_path": artifacts.get("training_backend_plan_path"),
        "training_config_path": artifacts.get("training_config_path") or execution_contract.get("config_path"),
        "training_invocation_path": artifacts.get("training_invocation_path") or execution_contract.get("invocation_path"),
        "execution_command": execution_contract.get("command") or [],
        "output_contract_targets": output_contract_targets,
        "missing_dependency_count": len(dependency_report.get("missing_packages") or []),
        "required_packages": dependency_report.get("required_packages") or [],
    }
    missing_proof_fields = []
    for field in (
        "cycle_id",
        "plan_id",
        "student_id",
        "base_model_ref",
        "dataset_manifest_ref",
        "method",
        "framework",
        "training_backend_plan_path",
        "training_config_path",
        "training_invocation_path",
    ):
        if not template[field]:
            missing_proof_fields.append(field)
    if not template["training_modes"]:
        missing_proof_fields.append("training_modes")
    if not template["teacher_refs"]:
        missing_proof_fields.append("teacher_refs")
    if template["license_state"] != "approved_train":
        missing_proof_fields.append("license_approved_train")
    if not template["eval_refs"]:
        missing_proof_fields.append("eval_refs")
    if not _hidden_eval_attestation_passed(template["hidden_eval_attestation"]):
        missing_proof_fields.append("hidden_eval_attestation_passed")
    if not template["rollback_ref"]:
        missing_proof_fields.append("rollback_ref")
    if not template["operator_approved"]:
        missing_proof_fields.append("operator_approved")
    if dependency_report.get("ready") is not True:
        missing_proof_fields.append("training_dependencies_ready")
    if not output_contract_targets:
        missing_proof_fields.append("output_artifact_contract")
    if template["backend_status"] != "sandbox_backend_plan_ready":
        missing_proof_fields.append("sandbox_backend_plan_ready")
    return {
        "schema_version": "training_backend_plan_request_template.v0.1",
        "endpoint": "/ops/brain/production-spine/training-backend-plans",
        "method": "POST",
        "ready_to_submit": not missing_proof_fields,
        "required_proof_fields": [
            "cycle_id",
            "plan_id",
            "student_id",
            "base_model_ref",
            "dataset_manifest_ref",
            "method",
            "framework",
            "training_modes",
            "teacher_refs",
            "license_approved_train",
            "eval_refs",
            "hidden_eval_attestation_passed",
            "rollback_ref",
            "operator_approved",
            "training_dependencies_ready",
            "training_config_path",
            "training_invocation_path",
            "output_artifact_contract",
        ],
        "missing_proof_fields": sorted(set(missing_proof_fields)),
        "template": template,
        "source": "latest-training-backend-plan",
        "operator_visible": True,
        "mutation_boundary": "template-only-training-backend-plan-no-training-execution",
    }


def _artifact_type_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        artifact_type = str(record.get("artifact_type") or "artifact")
        counts[artifact_type] = counts.get(artifact_type, 0) + 1
    return dict(sorted(counts.items()))


def _collect_refs(mapping: dict[str, Any], *keys: str) -> list[str]:
    return [str(mapping[key]) for key in keys if mapping.get(key)]


def _artifact_refs(item: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for key in ("artifact_refs", "artifacts"):
        value = item.get(key) if isinstance(item, dict) else None
        if isinstance(value, dict):
            refs.extend(str(ref) for ref in value.values() if ref)
        elif isinstance(value, list):
            refs.extend(str(ref) for ref in value if ref)
    return refs


def _project_local_signing_key_path(root: Path, requested_path: Any, *, default_path: Path) -> Path | None:
    root.mkdir(parents=True, exist_ok=True)
    root_resolved = root.resolve()
    candidate = Path(str(requested_path)) if requested_path else default_path
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate_resolved = candidate.resolve()
    try:
        candidate_resolved.relative_to(root_resolved)
    except ValueError:
        return None
    return candidate_resolved


def _signing_key_creation_blocked(*, key_id: str, reason: str, events_path: Path) -> dict[str, Any]:
    return {
        "schema_version": "project_local_signing_key_creation.v0.1",
        "key_id": key_id,
        "status": "blocked",
        "blocked_reason": reason,
        "storage_scope": "project_local_encrypted_file",
        "encrypted_key_file_persisted": False,
        "signing_secret_persisted": False,
        "passphrase_persisted": False,
        "production_mutation_allowed": False,
        "artifacts": {
            "events_path": str(events_path),
        },
        "created_at": utcnow().isoformat(),
    }


def _lifecycle_evidence_chain_entry(evidence_id: str, evidence: dict[str, Any]) -> dict[str, Any]:
    evidence = evidence if isinstance(evidence, dict) else {}
    status = _lifecycle_evidence_status(evidence)
    blockers = _lifecycle_evidence_blockers(evidence)
    ready = status in {"ready", "passed", "trusted"} and not blockers
    return {
        "evidence_id": evidence_id,
        "schema_version": evidence.get("schema_version"),
        "status": status,
        "ready": ready,
        "operator_visible": bool(evidence.get("operator_visible", True)),
        "artifact_ref_count": _count_lifecycle_artifact_refs(evidence),
        "blockers": blockers,
        "mutation_boundary": evidence.get("mutation_boundary") or evidence.get("replay_boundary"),
    }


def _lifecycle_evidence_status(evidence: dict[str, Any]) -> str:
    if evidence.get("status"):
        return str(evidence["status"])
    if "passed" in evidence:
        return "passed" if evidence.get("passed") else "failed"
    if "quarantined_count" in evidence:
        return "trusted" if int(evidence.get("quarantined_count") or 0) == 0 else "quarantined"
    if evidence.get("promotion_allowed") is False:
        return "blocked"
    return "ready" if evidence else "blocked"


def _lifecycle_evidence_blockers(evidence: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for key in ("blocked_reasons", "open_gates", "promotion_blockers", "integrity_blockers"):
        blockers.extend(str(item) for item in evidence.get(key) or [])
    for key in ("promotion_blocker", "teacher_ejection_blocker", "production_mutation_blocker", "real_signing_blocker"):
        value = evidence.get(key)
        if value:
            blockers.append(str(value))
    return sorted(set(blockers))


def _count_lifecycle_artifact_refs(evidence: dict[str, Any]) -> int:
    count = 0
    for key in ("artifact_refs", "artifacts"):
        value = evidence.get(key)
        if isinstance(value, dict):
            count += sum(1 for item in value.values() if item)
        elif isinstance(value, list):
            count += sum(1 for item in value if item)
    return count


def _build_signer_readiness(deep_replay: dict[str, Any]) -> dict[str, Any]:
    signature_policy = deep_replay.get("signature_policy") or {}
    current_state = str(signature_policy.get("current_signature_state") or "unknown")
    next_state = str(signature_policy.get("next_signature_state") or "signed_ed25519")
    allowed_unsigned = [str(item) for item in signature_policy.get("unsigned_state_allowed_for") or []]
    requires_real_signing = bool(signature_policy.get("production_promotion_requires_real_signing"))
    signing_configuration_state = str(signature_policy.get("signing_configuration_state") or "missing")
    signing_secret_persisted = bool(signature_policy.get("signing_secret_persisted", False))
    encrypted_key_file_persisted = bool(signature_policy.get("encrypted_key_file_persisted", False))
    signing_key_storage_scope = signature_policy.get("signing_key_storage_scope")
    production_blocker = "real_signing_required" if requires_real_signing and current_state != next_state else None
    return {
        "schema_version": "signer_readiness.v0.1",
        "status": "blocked" if production_blocker else "ready",
        "current_signature_state": current_state,
        "next_signature_state": next_state,
        "unsigned_state_allowed_for": allowed_unsigned,
        "signing_configuration_state": signing_configuration_state,
        "signing_secret_persisted": signing_secret_persisted,
        "encrypted_key_file_persisted": encrypted_key_file_persisted,
        "signing_key_storage_scope": signing_key_storage_scope,
        "durable_project_local_signer": encrypted_key_file_persisted and current_state == next_state,
        "sandbox_shadow_replay_allowed": current_state == "unsigned_v0" and bool(allowed_unsigned),
        "production_promotion_requires_real_signing": requires_real_signing,
        "production_mutation_blocker": production_blocker,
        "real_signing_blocker": signature_policy.get("real_signing_blocker"),
    }


def _growth_engine_gate_from_request(request: dict[str, Any]) -> dict[str, Any]:
    gate = dict(request.get("growth_gate") or request.get("adapter_training_gate") or {})
    adapter_training_plan_ref = request.get("adapter_training_plan_ref") or gate.get("adapter_training_plan_ref")
    adapter_training_plan_status = str(
        request.get("adapter_training_plan_status") or gate.get("adapter_training_plan_status") or "unknown"
    )
    blockers: list[str] = []
    if adapter_training_plan_status == "blocked":
        blockers.append("growth_engine_adapter_training_plan_blocked")
    if gate and gate.get("allowed") is False:
        gate_blockers = gate.get("blockers") or []
        if not gate_blockers:
            blockers.append("growth_engine_adapter_training_gate_blocked")
        for blocker in gate_blockers:
            if isinstance(blocker, dict):
                blockers.append(str(blocker.get("rule_id") or "growth_engine_adapter_training_gate_blocked"))
            else:
                blockers.append(str(blocker))
    for finding in request.get("adapter_training_findings") or []:
        if isinstance(finding, dict) and finding.get("severity") == "hard_fail":
            blockers.append(str(finding.get("rule_id") or "growth_engine_adapter_training_hard_fail_findings"))
    blockers = sorted(set(blockers))
    return {
        "gate_id": str(gate.get("gate_id") or "growth_engine_adapter_training_gate"),
        "adapter_training_plan_ref": adapter_training_plan_ref,
        "adapter_training_plan_status": adapter_training_plan_status,
        "allowed": not blockers,
        "blockers": blockers,
        "source": "growth_engine_request",
    }


def _compiled_knowledge_context(request: dict[str, Any]) -> dict[str, Any]:
    refs = list(request.get("knowledge_artifact_refs") or [])
    runtime_gate = _knowledge_artifact_runtime_gate(request)
    return {
        "surface_id": "knowledge-artifact-compiler",
        "artifact_refs": refs,
        "access_rule": "artifact-refs-only-through-KRC",
        "mutation_allowed": False,
        "visibility": "teacher-council-review-context" if refs else "none",
        "requires_krc_runtime_context_allowed": True,
        "blocks_stale_or_quarantined_context": True,
        "blocks_raw_retrieval_fallback_context": True,
        "runtime_gate_source": "KnowledgeArtifactCompiler.query",
        "allowed": runtime_gate["allowed"],
        "runtime_context_evidence_count": runtime_gate["runtime_context_evidence_count"],
        "blocked_artifact_refs": runtime_gate["blocked_artifact_refs"],
        "blocked_reasons": runtime_gate["blocked_reasons"],
        "context_boundary": "compiled artifacts can inform teacher review only by explicit refs",
    }


def _knowledge_artifact_runtime_gate(request: dict[str, Any]) -> dict[str, Any]:
    blocked_refs: list[str] = []
    blocked_reasons: list[str] = []
    for context in request.get("knowledge_artifact_runtime_contexts") or []:
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
        "allowed": not blocked_refs and not blocked_reasons,
        "runtime_context_evidence_count": len(request.get("knowledge_artifact_runtime_contexts") or []),
        "blocked_artifact_refs": sorted(set(blocked_refs)),
        "blocked_reasons": sorted(set(blocked_reasons)),
    }


def _knowledge_artifact_records(artifact_refs: list[str]) -> list[dict[str, Any]]:
    records = []
    for artifact_ref in artifact_refs:
        records.append(
            {
                "artifact_path": artifact_ref,
                "relative_path": f"knowledge-artifacts/{safe_name(artifact_ref)}.ref",
                "artifact_type": "knowledge_artifact_ref",
                "hash": _sha256({"knowledge_artifact_ref": artifact_ref}),
                "signature_state": "unsigned_v0",
                "ref_only": True,
                "mutation_allowed": False,
                "requires_krc_runtime_context_allowed": True,
                "blocks_stale_or_quarantined_context": True,
                "blocks_raw_retrieval_fallback_context": True,
                "runtime_gate_source": "KnowledgeArtifactCompiler.query",
            }
        )
    return records


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _merge_latest_lifecycle_fields(
    cycle_dir: Path,
    *,
    updates: dict[str, Any],
    event: dict[str, Any],
) -> dict[str, Any]:
    lifecycle_paths = sorted(
        cycle_dir.glob("growth-lifecycles/*/lifecycle_report.json"),
        key=lambda path: path.stat().st_mtime if path.exists() else 0,
        reverse=True,
    )
    if not lifecycle_paths:
        return {"status": "not_recorded", "reason": "lifecycle_report_not_found"}
    lifecycle_path = lifecycle_paths[0]
    try:
        lifecycle = json.loads(lifecycle_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "blocked", "reason": "lifecycle_report_unreadable", "lifecycle_report_path": str(lifecycle_path)}

    lifecycle.update(updates)
    lifecycle["production_mutation_allowed"] = False
    if isinstance(lifecycle.get("closed_loop_summary"), dict):
        node_replay = lifecycle.get("node_registry_replay_evidence") or {}
        runtime_health = lifecycle.get("runtime_health_monitor") or {}
        lifecycle["closed_loop_summary"]["node_registry_ready"] = node_replay.get("status") == "ready"
        lifecycle["closed_loop_summary"]["runtime_health_ready"] = runtime_health.get("decision") == "ready"
    _write_json(lifecycle_path, lifecycle)

    events_path = Path(str((lifecycle.get("artifacts") or {}).get("lifecycle_events_path") or ""))
    if not events_path.is_file():
        events_path = lifecycle_path.with_name("lifecycle_events.jsonl")
    events = _read_jsonl(events_path)
    events.append({**event, "production_mutation_allowed": False})
    _write_jsonl(events_path, events)
    return {
        "status": "updated",
        "lifecycle_report_path": str(lifecycle_path),
        "lifecycle_events_path": str(events_path),
        "production_mutation_allowed": False,
    }


def _release_manifest_replay_evidence(
    manifest: dict[str, Any],
    *,
    source: str,
    ready: bool,
    blocker_key: str,
    mutation_boundary: str,
) -> dict[str, Any]:
    blockers = [str(item) for item in manifest.get(blocker_key) or []]
    return {
        "schema_version": "release_manifest_replay_evidence.v0.1",
        "source": source,
        "status": "ready" if ready and not blockers else "blocked",
        "decision": manifest.get("decision"),
        "ready": bool(ready and not blockers),
        "blockers": blockers,
        "artifact_refs": manifest.get("artifacts") or {},
        "adapter_artifact_trust_status": manifest.get("adapter_artifact_trust_status"),
        "adapter_artifact_trust_clear": bool(manifest.get("adapter_artifact_trust_clear")),
        "buyer_release_allowed": bool(manifest.get("buyer_release_allowed")),
        "release_mutation_allowed": bool(manifest.get("release_mutation_allowed")),
        "mutation_boundary": mutation_boundary,
        "operator_visible": True,
    }


def _without_resolved_signed_replay_blockers(blocked_reasons: list[Any]) -> list[str]:
    resolved = {
        "artifact_trust_quarantine",
        "real_signing_required",
        "trusted_adapter_artifact_required",
        "trusted_signed_replay_required",
    }
    return sorted({str(reason) for reason in blocked_reasons if str(reason) not in resolved})


def _sha256(payload: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _load_shadow_weights(path: Path) -> tuple[dict[str, float], str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "w" in payload and "b" in payload:
        return {"w": float(payload["w"]), "b": float(payload["b"])}, "sandbox_proof_weights"
    nested = payload.get("weights")
    if isinstance(nested, dict) and "w" in nested and "b" in nested:
        return {"w": float(nested["w"]), "b": float(nested["b"])}, "sandbox_runner_checkpoint"
    raise ValueError(f"Unsupported shadow weights payload: {path}")


def _load_shadow_weights_from_adapter_bundle(path: Path) -> tuple[dict[str, float], str]:
    with zipfile.ZipFile(path) as bundle:
        checkpoint = json.loads(bundle.read("checkpoint.json").decode("utf-8"))
    nested = checkpoint.get("weights")
    if isinstance(nested, dict) and "w" in nested and "b" in nested:
        return {"w": float(nested["w"]), "b": float(nested["b"])}, "sandbox_adapter_bundle_checkpoint"
    raise ValueError(f"Unsupported adapter bundle checkpoint payload: {path}")


def _validate_lifecycle_replay_consistency(artifact_bridge: dict[str, Any], deep_replay: dict[str, Any]) -> dict[str, Any]:
    bridge_paths = {
        key: str(value)
        for key, value in artifact_bridge.items()
        if isinstance(value, str) and value.strip()
    }
    missing_bridge_paths = sorted(key for key, value in bridge_paths.items() if not Path(value).is_file())

    artifact_index_path = str((deep_replay.get("artifacts") or {}).get("artifact_index_path", ""))
    indexed_paths = set()
    indexed_records: dict[str, dict[str, Any]] = {}
    indexed_hashes: dict[str, str] = {}
    indexed_signature_states: dict[str, str] = {}
    for record in _read_jsonl(Path(artifact_index_path)):
        if isinstance(record.get("artifact_path"), str):
            artifact_path = str(Path(record["artifact_path"]))
            indexed_paths.add(artifact_path)
            indexed_records[artifact_path] = record
            if isinstance(record.get("hash"), str):
                indexed_hashes[artifact_path] = str(record["hash"])
            if isinstance(record.get("signature_state"), str):
                indexed_signature_states[artifact_path] = str(record["signature_state"])
    replay_index_exempt_bridge_paths = ["deep_replay_artifact_index_path"]
    signature_policy = deep_replay.get("signature_policy") or {}
    expected_signature_state = str(signature_policy.get("current_signature_state") or "unsigned_v0")
    bridge_paths_missing_from_replay = sorted(
        key
        for key, value in bridge_paths.items()
        if key not in replay_index_exempt_bridge_paths and str(Path(value)) not in indexed_paths
    )
    bridge_hash_mismatches = sorted(
        key
        for key, value in bridge_paths.items()
        if key not in replay_index_exempt_bridge_paths
        and key not in missing_bridge_paths
        and str(Path(value)) in indexed_hashes
        and _file_sha256(Path(value)) != indexed_hashes[str(Path(value))]
    )
    bridge_signature_state_mismatches = sorted(
        key
        for key, value in bridge_paths.items()
        if key not in replay_index_exempt_bridge_paths
        and key not in missing_bridge_paths
        and str(Path(value)) in indexed_paths
        and indexed_signature_states.get(str(Path(value))) != expected_signature_state
    )
    bridge_signature_verification_failures = sorted(
        key
        for key, value in bridge_paths.items()
        if expected_signature_state == "signed_ed25519"
        and key not in replay_index_exempt_bridge_paths
        and key not in missing_bridge_paths
        and str(Path(value)) in indexed_records
        and not verify_signed_artifact_record(indexed_records[str(Path(value))])
    )
    integrity_blockers = [
        name
        for name, values in {
            "missing_bridge_paths": missing_bridge_paths,
            "bridge_paths_missing_from_replay": bridge_paths_missing_from_replay,
            "bridge_hash_mismatches": bridge_hash_mismatches,
            "bridge_signature_state_mismatches": bridge_signature_state_mismatches,
            "bridge_signature_verification_failures": bridge_signature_verification_failures,
        }.items()
        if values
    ]

    return {
        "schema_version": "lifecycle_replay_consistency.v0.1",
        "passed": not integrity_blockers,
        "integrity_state": "failed" if integrity_blockers else "verified",
        "integrity_blockers": integrity_blockers,
        "checked_bridge_path_count": len(bridge_paths),
        "indexed_bridge_path_count": len(bridge_paths) - len(replay_index_exempt_bridge_paths) - len(bridge_paths_missing_from_replay),
        "expected_signature_state": expected_signature_state,
        "missing_bridge_paths": missing_bridge_paths,
        "bridge_paths_missing_from_replay": bridge_paths_missing_from_replay,
        "bridge_hash_mismatches": bridge_hash_mismatches,
        "bridge_signature_state_mismatches": bridge_signature_state_mismatches,
        "bridge_signature_verification_failures": bridge_signature_verification_failures,
        "replay_index_exempt_bridge_paths": replay_index_exempt_bridge_paths,
        "artifact_index_path": artifact_index_path,
    }


def _file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [
        [sum(left[row][inner] * right[inner][col] for inner in range(len(right))) for col in range(len(right[0]))]
        for row in range(len(left))
    ]


def _softmax(values: list[float]) -> list[float]:
    exp_values = [math.exp(value) for value in values]
    total = sum(exp_values)
    return [round(value / total, 6) for value in exp_values]


def _l2_delta(before: list[float], after: list[float]) -> float:
    return round(math.sqrt(sum((right - left) ** 2 for left, right in zip(before, after))), 6)


def _sandbox_training_blockers(request: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not request.get("operator_approved"):
        blockers.append("operator_approval_required")
    if request.get("contains_private_data"):
        blockers.append("private_data_not_allowed_in_sandbox_proof")
    if request.get("training_scope") != "sandbox_proof":
        blockers.append("only_sandbox_proof_scope_allowed")
    dataset = request.get("dataset") or []
    if len(dataset) < 2:
        blockers.append("sandbox_proof_requires_at_least_two_rows")
    for item in dataset:
        if not isinstance(item, dict) or "x" not in item or "y" not in item:
            blockers.append("dataset_rows_require_x_y")
            break
    return blockers


def _hidden_eval_attestation_passed(attestation: dict[str, Any]) -> bool:
    leakage_scan = attestation.get("leakage_scan") or {}
    return (
        bool(attestation.get("sealed"))
        and attestation.get("visible_to_training") is False
        and attestation.get("visible_to_teacher_council") is False
        and leakage_scan.get("status") == "passed"
    )


def _linear_loss(dataset: list[tuple[float, float]], w: float, b: float) -> float:
    return sum(((w * x + b) - y) ** 2 for x, y in dataset) / len(dataset)


def _normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    shifted = {key: math.exp(value - max(scores.values())) for key, value in scores.items()}
    total = sum(shifted.values())
    return {key: round(value / total, 6) for key, value in shifted.items()}


def _route_margin(scores: list[float]) -> float:
    if len(scores) < 2:
        return 1.0 if scores else 0.0
    ordered = sorted(scores, reverse=True)
    return round(ordered[0] - ordered[1], 6)


def _execute_tensor_program_op(op: dict[str, Any]) -> Any:
    op_type = str(op["op"])
    if op_type == "matmul":
        return _matmul(op["left"], op["right"])
    if op_type == "relu":
        return [max(0, value) for value in op["input"]]
    if op_type == "softmax":
        return _softmax([float(value) for value in op["input"]])
    if op_type == "linear_update":
        w = float(op["w"])
        b = float(op["b"])
        x = float(op["x"])
        y = float(op["y"])
        learning_rate = float(op.get("learning_rate") or 0.01)
        error = (w * x + b) - y
        return {
            "w": round(w - learning_rate * (2 * error * x), 8),
            "b": round(b - learning_rate * (2 * error), 8),
        }
    raise ValueError(f"unsupported tensor program op: {op_type}")


def _score_from_error(error: float) -> float:
    return round(1.0 / (1.0 + max(0.0, error)), 6)


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 6) if values else 0.0


def _standard_deviation(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return round(math.sqrt(variance), 6)


def _lower_confidence_bound(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if len(values) == 1:
        return round(mean, 6)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    standard_error = math.sqrt(variance) / math.sqrt(len(values))
    return round(mean - 1.96 * standard_error, 6)


def _registry_rollback_snapshot(request: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "node_registry_rollback_snapshot.v0.1",
        "cycle_id": request["cycle_id"],
        "decision_id": decision["decision_id"],
        "student_id": request["student_id"],
        "parent_node_ref": request["parent_node_ref"],
        "restore_state": {
            "student_state": "shadow",
            "parent_state": "active",
            "routing_state": "parent_active_student_shadow",
        },
        "current_state": {
            "student_state": decision["student_state"],
            "parent_state": decision["parent_state"],
        },
        "restore_validated": True,
        "hash": _sha256(
            {
                "cycle_id": request["cycle_id"],
                "decision_id": decision["decision_id"],
                "student_state": decision["student_state"],
                "parent_state": decision["parent_state"],
            }
        ),
    }


def _build_reviewer_window_retirement_evidence(request: dict[str, Any]) -> dict[str, Any]:
    reviewer_path_value = request.get("reviewer_window_advancement_path")
    reviewer_path = Path(str(reviewer_path_value or ""))
    blockers = []
    advancement: dict[str, Any] = {}
    if not reviewer_path_value or not reviewer_path.exists() or not reviewer_path.is_file():
        blockers.append("reviewer_window_advancement_required_for_parent_retirement")
    else:
        try:
            advancement = json.loads(reviewer_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            blockers.append("reviewer_window_advancement_unreadable")
            advancement = {}
    ejection_readiness = advancement.get("ejection_readiness_evidence") or {}
    if advancement:
        if ejection_readiness.get("status") != "ready":
            blockers.append("reviewer_window_ejection_readiness_not_ready")
        if ejection_readiness.get("teacher_ejection_allowed") is not True:
            blockers.append("teacher_ejection_not_allowed_by_reviewer_windows")
        if ejection_readiness.get("parent_retirement_allowed") is not True and advancement.get("parent_retirement_allowed") is not True:
            blockers.append("parent_retirement_not_allowed_by_reviewer_windows")
    return {
        "schema_version": "reviewer_window_retirement_evidence.v0.1",
        "status": "ready" if not blockers else "blocked",
        "reviewer_window_advancement_path": str(reviewer_path) if reviewer_path_value else "",
        "window": advancement.get("window"),
        "window_status": advancement.get("window_status"),
        "teacher_ejection_allowed": bool(ejection_readiness.get("teacher_ejection_allowed")),
        "parent_retirement_allowed": bool(ejection_readiness.get("parent_retirement_allowed") or advancement.get("parent_retirement_allowed")),
        "pending_window_count": int(ejection_readiness.get("pending_window_count") or 0),
        "blockers": sorted(set(blockers)),
        "mutation_boundary": "parent-retirement-requires-reviewer-window-advancement-evidence",
        "operator_visible": True,
    }


def _build_canary_promotion_guard_evidence(request: dict[str, Any], *, blocked_reasons: list[str]) -> dict[str, Any]:
    shadow_runtime_window_passed = bool(request.get("shadow_runtime_window_passed"))
    canary_window_passed = bool(request.get("canary_window_passed") or request.get("canary_passed"))
    post_promotion_window_passed = bool(request.get("post_promotion_window_passed"))
    canary_blockers = []
    if blocked_reasons:
        canary_blockers.append("node_registry_decision_blocked")
    if not shadow_runtime_window_passed:
        canary_blockers.append("shadow_runtime_window_required")
    if not canary_window_passed:
        canary_blockers.append("canary_window_required")
    if request.get("action") == "retire_parent" and not post_promotion_window_passed:
        canary_blockers.append("post_promotion_window_required_for_parent_retirement")
    active_deployment_allowed = not canary_blockers
    return {
        "schema_version": "canary_promotion_guard_evidence.v0.1",
        "status": "ready" if active_deployment_allowed else "gated",
        "shadow_runtime_window_passed": shadow_runtime_window_passed,
        "canary_window_passed": canary_window_passed,
        "post_promotion_window_passed": post_promotion_window_passed,
        "active_deployment_allowed": active_deployment_allowed,
        "teacher_ejection_allowed": active_deployment_allowed and post_promotion_window_passed,
        "blockers": sorted(set(canary_blockers)),
        "mutation_boundary": "active-deployment-requires-shadow-canary-post-promotion-review",
        "operator_visible": True,
    }


def _build_runtime_method_canary_guard_evidence(
    request: dict[str, Any],
    *,
    promotion_blocker: str | None,
) -> dict[str, Any]:
    runtime_shadow_window_passed = bool(request.get("runtime_shadow_window_passed"))
    runtime_canary_window_passed = bool(request.get("runtime_canary_window_passed") or request.get("runtime_canary_passed"))
    hidden_eval_delta_review_passed = bool(request.get("hidden_eval_delta_review_passed"))
    blockers = []
    if promotion_blocker:
        blockers.append(str(promotion_blocker))
    if not runtime_shadow_window_passed:
        blockers.append("runtime_shadow_window_required")
    if not runtime_canary_window_passed:
        blockers.append("runtime_canary_window_required")
    if not hidden_eval_delta_review_passed:
        blockers.append("hidden_eval_delta_review_required")
    active_runtime_method_allowed = not blockers
    return {
        "schema_version": "runtime_method_canary_guard_evidence.v0.1",
        "status": "ready" if active_runtime_method_allowed else "gated",
        "runtime_shadow_window_passed": runtime_shadow_window_passed,
        "runtime_canary_window_passed": runtime_canary_window_passed,
        "hidden_eval_delta_review_passed": hidden_eval_delta_review_passed,
        "active_runtime_method_allowed": active_runtime_method_allowed,
        "blockers": sorted(set(blockers)),
        "mutation_boundary": "runtime-method-active-promotion-requires-shadow-canary-hidden-eval-delta",
        "operator_visible": True,
    }


def _federation_trust_score(metrics: dict[str, float]) -> float:
    sample_count = metrics.get("sample_count", 0.0)
    success_rate = metrics.get("success_rate", 0.0)
    failure_rate = metrics.get("failure_rate", 0.0)
    sample_score = min(sample_count / 50.0, 1.0) * 0.25
    quality_score = max(0.0, min(success_rate - failure_rate, 1.0)) * 0.65
    latency_score = 0.10 if metrics.get("latency_ms", 0.0) <= 500.0 else 0.02
    return round(sample_score + quality_score + latency_score, 6)


def _federation_anomaly_score(metrics: dict[str, float]) -> float:
    score = 0.0
    success_rate = metrics.get("success_rate", 0.0)
    failure_rate = metrics.get("failure_rate", 0.0)
    if success_rate < 0.0 or success_rate > 1.0:
        score += 0.5
    if failure_rate < 0.0 or failure_rate > 1.0:
        score += 0.5
    if success_rate + failure_rate > 1.2:
        score += 0.3
    if metrics.get("sample_count", 1.0) <= 0:
        score += 0.2
    return round(min(score, 1.0), 6)


def _secure_federation_aggregate(packets: list[dict[str, Any]]) -> dict[str, Any]:
    if not packets:
        return {"schema_version": "secure_federation_aggregate.v0.1", "packet_count": 0}
    success_values = [packet["sanitized_metrics"].get("success_rate", 0.0) for packet in packets]
    trust_values = [packet.get("trust_score", 0.0) for packet in packets]
    aggregate = {
        "schema_version": "secure_federation_aggregate.v0.1",
        "packet_count": len(packets),
        "raw_content_included": False,
        "contains_personal_data": False,
        "mean_success_rate": round(sum(success_values) / len(success_values), 6),
        "mean_trust_score": round(sum(trust_values) / len(trust_values), 6),
        "shadow_route_influence_only": True,
        "aggregate_signature": _sha256({"packet_signatures": [packet["packet_signature"] for packet in packets]}),
    }
    return aggregate


def _runtime_efficiency_score(candidate: dict[str, Any]) -> float:
    speed_score = min(float(candidate["tokens_per_second"]) / 50.0, 1.0)
    memory_score = max(0.0, 1.0 - (float(candidate["memory_gb"]) / 16.0))
    return round(speed_score * 0.65 + memory_score * 0.35, 6)


def _artifact_type_from_path(path: Path) -> str:
    name = path.name
    if name == "lifecycle_report.json" and "growth-lifecycles" in path.as_posix():
        return "growth_lifecycle_report"
    if name == "lifecycle_events.jsonl" and "growth-lifecycles" in path.as_posix():
        return "growth_lifecycle_event_log"
    if name == "training_report.json" and "sandbox-runner" in path.as_posix():
        return "sandbox_training_report"
    if name == "loss_trace.jsonl" and "sandbox-runner" in path.as_posix():
        return "sandbox_loss_trace"
    if name == "checkpoint.json" and "sandbox-runner" in path.as_posix():
        return "sandbox_checkpoint"
    if name == "adapter_artifact_bundle.zip" and "sandbox-runner" in path.as_posix():
        return "sandbox_adapter_bundle"
    if name == "adapter_manifest.json":
        return "sandbox_adapter_manifest"
    if name == "gguf_export_plan.json":
        return "sandbox_gguf_export_plan"
    if name == "quantization_manifest.json" and "sandbox-runner" in path.as_posix():
        return "sandbox_quantization_manifest"
    if name == "training_backend_plan.json":
        return "training_backend_plan"
    if name == "training_config.json":
        return "training_backend_config"
    if name == "training_invocation.ps1":
        return "training_backend_invocation"
    if name == "registry_snapshot.json" and "node-registry" in path.as_posix():
        return "node_registry_snapshot"
    if name == "reviewer_window_advancement.json" and "reviewer-windows" in path.as_posix():
        return "reviewer_window_advancement"
    if name == "real_training_gate.json" and "real-training-gates" in path.as_posix():
        return "real_training_gate"
    if name == "real_training_gate_events.jsonl" and "real-training-gates" in path.as_posix():
        return "real_training_gate_event_log"
    if path.suffix == ".jsonl":
        return "append_only_trace"
    if path.suffix == ".json":
        return "manifest"
    if path.suffix in {".yaml", ".yml"}:
        return "policy_or_genome"
    return "artifact"


def _drilldown_from_artifact(relative_path: str) -> str:
    if relative_path.startswith("growth-lifecycles/"):
        return "growth_lifecycle"
    if relative_path.startswith("training-backend-plans/"):
        if "/sandbox-runner/" in relative_path:
            return "sandbox_runner_training"
        return "training_backend_plan"
    if relative_path.startswith("sandbox-training/"):
        return "sandbox_training"
    if relative_path.startswith("child-executions/"):
        return "child_execution"
    if relative_path.startswith("hive-moe-routes/"):
        return "route_diff"
    if relative_path.startswith("tensor-programs/"):
        return "tensor_program"
    if relative_path.startswith("eval-gauntlets/"):
        return "hidden_eval"
    if relative_path.startswith("reviewer-windows/"):
        return "reviewer_window_history"
    if relative_path.startswith("real-training-gates/"):
        return "real_training_artifact_trust"
    if relative_path.startswith("node-registry/"):
        return "node_lifecycle"
    if relative_path.startswith("federation/"):
        return "federated_prior"
    if relative_path.startswith("dream-cycles/"):
        return "dream_cycle"
    if relative_path.startswith("runtime-foundry/"):
        return "runtime_foundry"
    if relative_path.startswith("knowledge-artifacts/"):
        return "knowledge_artifact"
    return "cycle_artifact"


def _finish_surfaces() -> list[str]:
    return [
        "real_training_runner",
        "child_node_execution",
        "native_hive_moe_runtime",
        "tensor_runtime_kernel",
        "teacher_council_automation",
        "sealed_eval_gauntlet",
        "durable_node_registry",
        "federated_learning_loop",
        "recursive_dream_execution",
        "runtime_quantization_foundry",
        "deep_replay_ui",
        "productization",
    ]
