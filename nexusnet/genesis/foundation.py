from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from nexusnet.canon.contracts import CANON_CONTRACT_SOURCE_REFS, build_canon_source_manifest


GENESIS_FOUNDATION_SURFACE_ID = "nexusnet-genesis-foundation-status"
GENESIS_BUILD_ORDER_REF = "docs/superpowers/specs/2026-07-05-nexusnet-genesis-build-order-design.md"
LAYER4_LEDGER_SPECS = (
    ("hive_activation", "latest_forward_pass", ("activation",), ("activation_id",)),
    ("sensory_input", "latest_sensory_input", (), ("sensory_ledger_id",)),
    ("embedding_tensor", "latest_embedding_tensor", (), ("embedding_ledger_id",)),
    ("temporal_positional", "latest_temporal_positional", (), ("temporal_ledger_id",)),
    ("memory_engram", "latest_memory_engram", (), ("memory_ledger_id",)),
    ("attention_routing", "latest_attention_routing", (), ("attention_ledger_id",)),
    ("residual_normalization", "latest_residual_normalization", (), ("normalization_ledger_id",)),
    ("sparse_expert_gate", "latest_sparse_expert_gate", (), ("gate_ledger_id",)),
    ("feedforward_expert", "latest_feedforward_expert", (), ("feedforward_ledger_id",)),
    ("laminar_microcircuit", "latest_laminar_microcircuit", (), ("microcircuit_id",)),
    ("neural_pathway", "latest_neural_pathway", (), ("pathway_id",)),
    ("synaptic_transmission", "latest_synaptic_transmission", (), ("transmission_id",)),
    ("neuroplastic_weight", "latest_neuroplastic_weight", (), ("weight_ledger_id",)),
    ("neuromodulatory_state", "latest_neuromodulatory_state", (), ("neuromodulator_id",)),
    ("latent_loop_exit", "latest_latent_loop_exit", (), ("latent_loop_id",)),
    ("kv_cache_compression", "latest_kv_cache_compression", (), ("kv_cache_ledger_id",)),
    ("loss_backpropagation", "latest_loss_backpropagation", (), ("backpropagation_id",)),
    ("optimizer_school", "latest_optimizer_school", (), ("optimizer_ledger_id",)),
    ("computational_graph", "latest_computational_graph", (), ("graph_ledger_id",)),
    ("model_genome", "latest_model_genome", (), ("genome_ledger_id",)),
    ("tensor_runtime_kernel", "latest_tensor_runtime_kernel", (), ("tensor_kernel_ledger_id",)),
    ("layer_block_stack", "latest_layer_block_stack", (), ("layer_stack_ledger_id",)),
    ("durable_storage", "latest_durable_storage", (), ("storage_ledger_id",)),
    ("checkpoint_coverage", "latest_checkpoint_coverage", (), ("coverage_ledger_id",)),
    ("runtime_decision", "latest_runtime_decision", (), ("runtime_decision_id",)),
    ("backend_quantization_execution", "latest_backend_quantization_execution", (), ("backend_execution_id",)),
)


class GenesisFoundationStatusService:
    """Read-only Genesis foundation status for canon Layers 0-4."""

    def __init__(self, *, artifacts_dir: Path | str, project_root: Path | str, hive_substrate: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.project_root = Path(project_root)
        self.hive_substrate = hive_substrate
        self.repo_root = Path(__file__).resolve().parents[2]
        self.foundation_dir = self.artifacts_dir / "genesis" / "foundation"
        self.event_ledger_path = self.foundation_dir / "neural_bus_events.jsonl"

    def summary(self, session_id: str | None = None) -> dict[str, Any]:
        source_manifest = build_canon_source_manifest(self.project_root)
        source_authority_chain = self._source_authority_chain(source_manifest)
        loaded_count = sum(1 for source in source_authority_chain if source["status"] == "ingested")
        layer4_spine = self._layer4_neural_substrate_ledger_spine(session_id=session_id)
        foundation_seed = self._foundation_seed(
            source_manifest=source_manifest,
            source_authority_chain=source_authority_chain,
            loaded_count=loaded_count,
            layer4_spine=layer4_spine,
        )
        foundation_digest = _digest(foundation_seed)
        artifact_ref = f"genesis-foundation::{foundation_digest}"
        event_ref = f"neural-bus-event::{foundation_digest}"
        self._ensure_event_record(event_ref=event_ref, artifact_ref=artifact_ref)
        projection = self._neural_projection(
            artifact_ref=artifact_ref,
            event_ref=event_ref,
            event_count=self._event_count(),
        )
        payload = self._payload(
            artifact_ref=artifact_ref,
            source_manifest=source_manifest,
            source_authority_chain=source_authority_chain,
            loaded_count=loaded_count,
            projection=projection,
            layer4_spine=layer4_spine,
        )
        artifact_path = self.foundation_dir / f"{foundation_digest}.json"
        if artifact_path.is_file():
            persisted = _read_json(artifact_path)
            if isinstance(persisted, dict) and persisted.get("surface_id") == GENESIS_FOUNDATION_SURFACE_ID:
                persisted["replay"] = self._replay(artifact_ref=artifact_ref, status="replayed")
                return persisted
        self.foundation_dir.mkdir(parents=True, exist_ok=True)
        payload["replay"] = self._replay(artifact_ref=artifact_ref, status="recorded")
        artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return payload

    def _payload(
        self,
        *,
        artifact_ref: str,
        source_manifest: dict[str, Any],
        source_authority_chain: list[dict[str, Any]],
        loaded_count: int,
        projection: dict[str, Any],
        layer4_spine: dict[str, Any],
    ) -> dict[str, Any]:
        evidence_refs = [
            artifact_ref,
            "canon-source-manifest::whole-project-canon-source-manifest",
            "authority::NexusBrain",
            "harness-preflight::non-mutating",
            "permission-isolation::read-only",
            projection["typed_event_envelope"]["event_ref"],
            projection["hive_blackboard_snapshot"]["snapshot_ref"],
            projection["plane_trace"]["trace_ref"],
            *layer4_spine.get("evidence_refs", []),
        ]
        return {
            "schema_version": "nexusnet-genesis-foundation-status-v1",
            "surface_id": GENESIS_FOUNDATION_SURFACE_ID,
            "status_label": "LOCKED CANON",
            "honest_status_label": "genesis-layers-0-to-3-live-control-plane-not-production-approved",
            "authority": "NexusBrain",
            "foundation_scope": "whole-project",
            "product_surface": "release-harness",
            "source_authority_chain": source_authority_chain,
            "canon_source_manifest": source_manifest,
            "addendum_ledger_manifest": self._addendum_ledger_manifest(source_authority_chain),
            "repo_state_evidence": self._repo_state_evidence(),
            "build_layers": self._build_layers(artifact_ref=artifact_ref, layer4_spine=layer4_spine),
            "harness_preflight": self._harness_preflight(
                source_authority_chain=source_authority_chain,
                loaded_count=loaded_count,
            ),
            "nexusbrain_authority_envelope": self._authority_envelope(),
            "authority_receipt": self._authority_receipt(artifact_ref=artifact_ref),
            "permission_isolation_receipt": self._permission_isolation_receipt(artifact_ref=artifact_ref),
            "neural_bus_hive_blackboard_projection": projection,
            "layer4_neural_substrate_ledger_spine": layer4_spine,
            "evidence_refs": _dedupe(evidence_refs)[:80],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-canon-source-refs-hashes-counts-layer-statuses-receipt-ids-and-artifact-refs-only-"
                "no-raw-canon-text-prompts-outputs-session-ids-or-local-paths"
            ),
            "mutation_boundary": "genesis-foundation-status-and-event-receipts-only-no-active-production-mutation",
        }

    def _source_authority_chain(self, source_manifest: dict[str, Any]) -> list[dict[str, Any]]:
        source_records = {
            str(source.get("source_ref") or ""): source for source in source_manifest.get("sources", [])
        }
        chain: list[dict[str, Any]] = []
        for priority, source_ref in enumerate(CANON_CONTRACT_SOURCE_REFS, start=1):
            record = source_records.get(source_ref, {})
            chain.append(
                {
                    "priority": priority,
                    "source_ref": source_ref,
                    "source_role": _source_role(source_ref),
                    "status": str(record.get("status") or "missing"),
                    "sha256": record.get("sha256"),
                    "byte_count": int(record.get("byte_count") or 0),
                    "raw_content_included": False,
                }
            )
        plan_record = self._source_ref_record(GENESIS_BUILD_ORDER_REF, priority=len(chain) + 1)
        plan_record["source_role"] = "approved-build-order-design"
        chain.append(plan_record)
        return chain

    def _source_ref_record(self, source_ref: str, *, priority: int) -> dict[str, Any]:
        for root in (self.project_root, self.repo_root):
            path = root / source_ref
            if path.is_file():
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                return {
                    "priority": priority,
                    "source_ref": source_ref,
                    "source_role": "implementation-method",
                    "status": "ingested",
                    "sha256": f"sha256:{digest}",
                    "byte_count": path.stat().st_size,
                    "raw_content_included": False,
                }
        return {
            "priority": priority,
            "source_ref": source_ref,
            "source_role": "implementation-method",
            "status": "missing",
            "sha256": None,
            "byte_count": 0,
            "raw_content_included": False,
        }

    def _addendum_ledger_manifest(self, source_authority_chain: list[dict[str, Any]]) -> dict[str, Any]:
        addendum_refs = [
            source["source_ref"]
            for source in source_authority_chain
            if "ADDENDUM" in source["source_ref"] or "LEDGER" in source["source_ref"]
        ]
        assimilation_refs = [
            source["source_ref"]
            for source in source_authority_chain
            if "assimilation" in source["source_ref"].lower()
        ]
        return {
            "schema_version": "nexusnet-genesis-addendum-ledger-manifest-v1",
            "surface_id": "genesis-addendum-ledger-manifest",
            "addendum_refs": addendum_refs,
            "assimilation_refs": assimilation_refs,
            "accepted_status_labels": [
                "planned",
                "candidate",
                "shadow",
                "live-control-plane",
                "live-substrate",
                "blocked",
                "side-barred",
                "rejected",
                "superseded",
                "production-approved",
            ],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }

    def _repo_state_evidence(self) -> dict[str, Any]:
        return {
            "schema_version": "nexusnet-genesis-repo-state-evidence-v1",
            "surface_id": "genesis-repo-state-evidence",
            "expected_gitnexus_repo": "NexusNet",
            "gitnexus_unknown_label_allowed": False,
            "project_root_boundary": "local-project-root-only",
            "dirty_worktree_policy": "do-not-revert-unrelated-user-changes",
            "symbol_edit_policy": "gitnexus-impact-required-before-symbol-edits",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }

    def _build_layers(self, *, artifact_ref: str, layer4_spine: dict[str, Any]) -> list[dict[str, Any]]:
        layers = [
            self._layer(
                layer_id="layer-0-canon-repo-truth",
                label="Canon, addendum, ledger, and repository truth",
                typed_contract_ref="genesis-contract::canon-source-manifest",
                evidence_refs=[artifact_ref, "canon-source-manifest::whole-project-canon-source-manifest"],
                blocker_refs=[],
            ),
            self._layer(
                layer_id="layer-1-harness-identity-authority",
                label="Harness contract, agent identity, and NexusBrain authority",
                typed_contract_ref="genesis-contract::harness-preflight-authority-envelope",
                evidence_refs=[artifact_ref, "harness-preflight::non-mutating", "authority::NexusBrain"],
                blocker_refs=["production-mutation-requires-admin-approval"],
            ),
            self._layer(
                layer_id="layer-2-authority-isolation-fabric",
                label="Authority and isolation fabric",
                typed_contract_ref="genesis-contract::permission-isolation-receipt",
                evidence_refs=[artifact_ref, "permission-isolation::read-only"],
                blocker_refs=["ambient-credentials-denied", "unsafe-scope-fail-closed"],
            ),
            self._layer(
                layer_id="layer-3-neural-bus-blackboard-plane-trace",
                label="Neural Bus, HiveBlackboard, and plane trace",
                typed_contract_ref="genesis-contract::neural-bus-hive-blackboard-plane-trace",
                evidence_refs=[artifact_ref, "neural-bus-event-ledger::genesis-foundation"],
                blocker_refs=["downstream-consumption-requires-artifact-ref"],
            ),
        ]
        layer4_status = str(layer4_spine.get("status") or "not-observed")
        if layer4_status in {"live-substrate", "degraded"}:
            layer4_blockers = [str(ref) for ref in layer4_spine.get("blockers", [])]
            layer4_blockers.extend(
                f"missing_layer4_ledger::{ledger_id}"
                for ledger_id in layer4_spine.get("missing_ledger_ids", [])
            )
            layers.append(
                self._layer(
                    layer_id="layer-4-neural-substrate-ledger-spine",
                    label="Neural substrate ledger spine",
                    typed_contract_ref="genesis-contract::layer4-neural-substrate-ledger-spine",
                    evidence_refs=[
                        str(layer4_spine.get("source_hive_run_ref") or ""),
                        *[str(ref) for ref in layer4_spine.get("evidence_refs", [])],
                    ],
                    blocker_refs=layer4_blockers,
                    status=layer4_status,
                    honest_status_label=(
                        "live-substrate-not-production-approved"
                        if layer4_status == "live-substrate"
                        else "degraded-substrate-not-production-approved"
                    ),
                )
            )
        return layers

    def _layer(
        self,
        *,
        layer_id: str,
        label: str,
        typed_contract_ref: str,
        evidence_refs: list[str],
        blocker_refs: list[str],
        status: str = "live-control-plane",
        honest_status_label: str = "live-control-plane-not-production-approved",
    ) -> dict[str, Any]:
        return {
            "layer_id": layer_id,
            "label": label,
            "status": status,
            "honest_status_label": honest_status_label,
            "typed_contract_ref": typed_contract_ref,
            "source_refs": [
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md",
                GENESIS_BUILD_ORDER_REF,
            ],
            "evidence_refs": _dedupe(evidence_refs),
            "blocker_refs": blocker_refs,
            "production_approved": False,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }

    def _harness_preflight(
        self,
        *,
        source_authority_chain: list[dict[str, Any]],
        loaded_count: int,
    ) -> dict[str, Any]:
        required_refs = [source["source_ref"] for source in source_authority_chain]
        missing_refs = [
            source["source_ref"]
            for source in source_authority_chain
            if source["status"] != "ingested"
        ]
        return {
            "schema_version": "nexusnet-genesis-harness-preflight-v1",
            "surface_id": "genesis-harness-contract-preflight",
            "mode": "non-mutating",
            "decision": "review-required",
            "required_artifact_count": len(required_refs),
            "loaded_artifact_count": loaded_count,
            "missing_artifact_count": len(missing_refs),
            "missing_source_refs": missing_refs,
            "harness_adherence_evidence": [
                "AGENTS.md::gitnexus-impact-required",
                "superpowers::test-driven-development",
                "superpowers::verification-before-completion",
            ],
            "raw_secret_material_loaded": False,
            "unsafe_scope_blockers": ["production-mutation", "ambient-credentials", "raw-secret-material"],
            "active_production_mutation_allowed": False,
            "raw_content_included": False,
        }

    def _authority_envelope(self) -> dict[str, Any]:
        return {
            "schema_version": "nexusnet-genesis-nexusbrain-authority-envelope-v1",
            "surface_id": "genesis-nexusbrain-authority-envelope",
            "authority": "NexusBrain",
            "mother_brain_owned": True,
            "decision_envelope": {
                "decision_authority": "NexusBrain",
                "default_decision": "review-required",
                "refusal_power": True,
                "raw_content_included": False,
            },
            "parent_child_brain_contract": {
                "parent_ref": "NexusBrain",
                "child_ref_policy": "child-brain-must-carry-parent-ref-and-approval-gate",
                "mother_brain_approval_gate": "required-before-retention-mutation-or-production-promotion",
                "raw_content_included": False,
            },
            "allowed_action_classes": ["read-status", "record-sanitized-receipt", "record-sanitized-event"],
            "denied_action_classes": ["production-mutation", "raw-secret-access", "ambient-credential-use"],
            "active_production_mutation_allowed": False,
            "raw_content_included": False,
        }

    def _authority_receipt(self, *, artifact_ref: str) -> dict[str, Any]:
        return {
            "schema_version": "nexusnet-genesis-authority-receipt-v1",
            "surface_id": "genesis-authority-receipt",
            "receipt_id": f"authority-receipt::{_digest(artifact_ref)}",
            "decision_authority": "NexusBrain",
            "decision": "review-required",
            "allowed_action_classes": ["read-status", "record-sanitized-receipt", "record-sanitized-event"],
            "denied_action_classes": ["production-mutation", "raw-secret-access", "ambient-credential-use"],
            "evidence_refs": [artifact_ref, "authority::NexusBrain"],
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
        }

    def _permission_isolation_receipt(self, *, artifact_ref: str) -> dict[str, Any]:
        return {
            "schema_version": "nexusnet-genesis-permission-isolation-receipt-v1",
            "surface_id": "genesis-permission-isolation-receipt",
            "receipt_id": f"permission-isolation::{_digest(artifact_ref)}",
            "sandbox_tier": "read-only",
            "capability_scope": "status-artifact-and-sanitized-event-only",
            "ambient_credentials_allowed": False,
            "capability_token_required_for_mutation": True,
            "fail_closed": True,
            "tool_allowlist": ["read-local-canon-source-metadata", "write-sanitized-genesis-artifact"],
            "tool_denylist": ["production-file-mutation", "network-secret-access", "ambient-credential-use"],
            "evidence_refs": [artifact_ref, "permission-isolation::read-only"],
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
        }

    def _layer4_neural_substrate_ledger_spine(self, *, session_id: str | None) -> dict[str, Any]:
        if self.hive_substrate is None:
            return self._empty_layer4_spine(status="not-configured", blockers=["hive_substrate_not_configured"])
        try:
            summary = self.hive_substrate.summary(session_id=session_id)
        except Exception as exc:  # pragma: no cover - degraded status boundary for runtime services
            return self._empty_layer4_spine(
                status="degraded",
                blockers=[f"hive_substrate_summary_failed::{type(exc).__name__}"],
            )
        latest_forward = summary.get("latest_forward_pass") if isinstance(summary.get("latest_forward_pass"), dict) else {}
        source_ref = str(latest_forward.get("source_ref") or "")
        accepted_source_prefixes = ("nexusbrain-generate::", "nexusbrain-wrapped-model::")
        if not source_ref.startswith(accepted_source_prefixes):
            return self._empty_layer4_spine(status="not-observed", blockers=["nexusbrain_owned_hive_forward_pass_missing"])
        source = "nexusbrain-wrapped-model" if source_ref.startswith("nexusbrain-wrapped-model::") else "nexusbrain-generate"
        source_metadata = latest_forward.get("metadata") if isinstance(latest_forward.get("metadata"), dict) else {}
        source_brain_generate_status = str(source_metadata.get("brain_generate_status") or "")
        source_critique_status = str(source_metadata.get("critique_status") or "")
        source_degraded = source_brain_generate_status in {
            "blocked",
            "error",
            "failed",
            "runtime-unavailable",
        }

        ledgers = [self._layer4_ledger_record(summary, spec) for spec in LAYER4_LEDGER_SPECS]
        covered_ledgers = [ledger for ledger in ledgers if ledger["status"] == "covered"]
        missing_ledgers = [ledger["ledger_id"] for ledger in ledgers if ledger["status"] != "covered"]
        runtime_receipt = (
            summary.get("latest_runtime_growth_receipt")
            if isinstance(summary.get("latest_runtime_growth_receipt"), dict)
            else {}
        )
        runtime_packet = (
            summary.get("latest_runtime_growth_packet")
            if isinstance(summary.get("latest_runtime_growth_packet"), dict)
            else {}
        )
        project_heartbeat = (
            summary.get("project_heartbeat")
            if isinstance(summary.get("project_heartbeat"), dict)
            else {}
        )
        hive_run_id = str(latest_forward.get("run_id") or "")
        evidence_refs = _dedupe(
            [
                f"hive-forward::{hive_run_id}" if hive_run_id else "",
                str(project_heartbeat.get("heartbeat_id") or ""),
                str(runtime_receipt.get("receipt_id") or ""),
                str(runtime_packet.get("packet_id") or ""),
                *[str(ledger.get("artifact_ref") or "") for ledger in covered_ledgers],
            ]
        )
        blockers = (
            [f"nexusbrain_generate_status::{source_brain_generate_status}"]
            if source_degraded
            else []
        )
        status = "live-substrate" if not missing_ledgers and not source_degraded else "degraded"
        return {
            "schema_version": "nexusnet-genesis-layer4-neural-substrate-ledger-spine-v1",
            "surface_id": "genesis-layer4-neural-substrate-ledger-spine",
            "status": status,
            "honest_status_label": (
                "layer4-native-hive-substrate-ledgers-replayed"
                if status == "live-substrate"
                else "layer4-native-hive-substrate-ledgers-degraded"
            ),
            "source": source,
            "source_brain_generate_status": source_brain_generate_status or None,
            "source_critique_status": source_critique_status or None,
            "source_hive_run_id": hive_run_id or None,
            "source_hive_run_ref": f"hive-forward::{hive_run_id}" if hive_run_id else None,
            "project_heartbeat_id": project_heartbeat.get("heartbeat_id"),
            "runtime_growth_receipt_id": runtime_receipt.get("receipt_id"),
            "federated_packet_id": runtime_packet.get("packet_id"),
            "required_ledger_count": len(ledgers),
            "covered_ledger_count": len(covered_ledgers),
            "missing_ledger_ids": missing_ledgers,
            "blockers": blockers,
            "ledgers": ledgers,
            "evidence_refs": evidence_refs[:60],
            "raw_content_included": False,
            "contains_personal_data": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-hive-run-ledger-ids-surface-ids-counts-and-artifact-refs-only-no-prompts-"
                "outputs-session-ids-or-local-paths"
            ),
            "mutation_boundary": "layer4-substrate-ledger-status-only-no-active-production-mutation",
        }

    def _empty_layer4_spine(self, *, status: str, blockers: list[str]) -> dict[str, Any]:
        return {
            "schema_version": "nexusnet-genesis-layer4-neural-substrate-ledger-spine-v1",
            "surface_id": "genesis-layer4-neural-substrate-ledger-spine",
            "status": status,
            "honest_status_label": "layer4-native-hive-substrate-ledgers-not-observed",
            "source": None,
            "source_brain_generate_status": None,
            "source_critique_status": None,
            "source_hive_run_id": None,
            "source_hive_run_ref": None,
            "project_heartbeat_id": None,
            "runtime_growth_receipt_id": None,
            "federated_packet_id": None,
            "required_ledger_count": len(LAYER4_LEDGER_SPECS),
            "covered_ledger_count": 0,
            "missing_ledger_ids": [spec[0] for spec in LAYER4_LEDGER_SPECS],
            "blockers": blockers,
            "ledgers": [],
            "evidence_refs": [],
            "raw_content_included": False,
            "contains_personal_data": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def _layer4_ledger_record(self, summary: dict[str, Any], spec: tuple[str, str, tuple[str, ...], tuple[str, ...]]) -> dict[str, Any]:
        ledger_id, summary_key, nested_keys, id_keys = spec
        record = summary.get(summary_key) if isinstance(summary.get(summary_key), dict) else {}
        for nested_key in nested_keys:
            record = record.get(nested_key) if isinstance(record.get(nested_key), dict) else {}
        artifact_ref = _first_present(record, id_keys)
        surface_id = str(record.get("surface_id") or f"hive-{ledger_id.replace('_', '-')}-ledger")
        return {
            "ledger_id": ledger_id,
            "surface_id": surface_id,
            "status": "covered" if artifact_ref else "degraded",
            "artifact_ref": artifact_ref,
            "source_hive_run_ref": f"hive-forward::{record.get('run_id')}" if record.get("run_id") else None,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }

    def _neural_projection(self, *, artifact_ref: str, event_ref: str, event_count: int) -> dict[str, Any]:
        event_digest = _digest(event_ref)
        return {
            "schema_version": "nexusnet-genesis-neural-bus-hive-blackboard-projection-v1",
            "surface_id": "genesis-neural-bus-hive-blackboard-projection",
            "typed_event_envelope": {
                "schema_version": "nexusnet-neural-bus-event-envelope-v1",
                "event_ref": event_ref,
                "event_type": "genesis.foundation.status",
                "activation_ref": f"activation::{event_digest}",
                "correlation_ref": artifact_ref,
                "event_privacy_label": "sanitized-foundation-status",
                "artifact_bound": True,
                "raw_content_included": False,
            },
            "event_ledger": {
                "schema_version": "nexusnet-neural-bus-event-ledger-v1",
                "surface_id": "genesis-neural-bus-event-ledger",
                "mode": "append-only-file-backed",
                "event_count": event_count,
                "latest_event_ref": event_ref,
                "ledger_ref": "genesis-foundation-neural-bus-events",
                "raw_content_included": False,
            },
            "hive_blackboard_snapshot": {
                "schema_version": "nexusnet-hive-blackboard-snapshot-v1",
                "snapshot_ref": f"hive-blackboard::{event_digest}",
                "state": "foundation-status-projected",
                "priority_trails": [
                    {
                        "topic": "genesis-foundation",
                        "strength": 1.0,
                        "artifact_ref": artifact_ref,
                    }
                ],
                "raw_content_included": False,
            },
            "plane_trace": {
                "schema_version": "nexusnet-plane-trace-ledger-v1",
                "trace_ref": f"plane-trace::{event_digest}",
                "planes": ["canon", "authority", "isolation", "event"],
                "artifact_bound_downstream_consumption_required": True,
                "raw_content_included": False,
            },
            "evidence_refs": [artifact_ref, event_ref, f"hive-blackboard::{event_digest}", f"plane-trace::{event_digest}"],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def _ensure_event_record(self, *, event_ref: str, artifact_ref: str) -> None:
        self.foundation_dir.mkdir(parents=True, exist_ok=True)
        if self.event_ledger_path.is_file():
            for line in self.event_ledger_path.read_text(encoding="utf-8").splitlines():
                if event_ref in line:
                    return
        event = {
            "schema_version": "nexusnet-neural-bus-event-envelope-v1",
            "event_ref": event_ref,
            "event_type": "genesis.foundation.status",
            "correlation_ref": artifact_ref,
            "event_privacy_label": "sanitized-foundation-status",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }
        with self.event_ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    def _event_count(self) -> int:
        if not self.event_ledger_path.is_file():
            return 0
        return len([line for line in self.event_ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()])

    def _foundation_seed(
        self,
        *,
        source_manifest: dict[str, Any],
        source_authority_chain: list[dict[str, Any]],
        loaded_count: int,
        layer4_spine: dict[str, Any],
    ) -> str:
        seed = {
            "surface_id": GENESIS_FOUNDATION_SURFACE_ID,
            "source_manifest": source_manifest,
            "source_authority_chain": source_authority_chain,
            "loaded_count": loaded_count,
            "layer4_spine": {
                "status": layer4_spine.get("status"),
                "source_hive_run_ref": layer4_spine.get("source_hive_run_ref"),
                "evidence_refs": layer4_spine.get("evidence_refs", []),
                "covered_ledger_count": layer4_spine.get("covered_ledger_count"),
            },
            "layers": [
                "layer-0-canon-repo-truth",
                "layer-1-harness-identity-authority",
                "layer-2-authority-isolation-fabric",
                "layer-3-neural-bus-blackboard-plane-trace",
                "layer-4-neural-substrate-ledger-spine",
            ],
        }
        return json.dumps(seed, sort_keys=True, default=str)

    def _replay(self, *, artifact_ref: str, status: str) -> dict[str, Any]:
        return {
            "schema_version": "nexusnet-genesis-foundation-replay-v1",
            "surface_id": "genesis-foundation-replay",
            "status": status,
            "latest_artifact_ref": artifact_ref,
            "artifact_ref_kind": "content-addressed-sanitized-status",
            "artifact_path_digest": f"sha256:{_digest(artifact_ref + ':artifact-path')}",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }


def _source_role(source_ref: str) -> str:
    if "COMPLETE_CHAT_CANON_BOOK" in source_ref:
        return "primary-canon-book"
    if "POST_BOOK_CANON_ADDENDUM" in source_ref:
        return "post-book-canon-addendum"
    if "IMPLEMENTATION_LEDGER" in source_ref:
        return "canon-implementation-ledger"
    if "assimilation" in source_ref.lower():
        return "assimilation-ledger-or-gap-report"
    return "canon-addendum-or-research-detail"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _first_present(record: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = record.get(key)
        if value:
            return str(value)
    return None


def _dedupe(values: list[str | None]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            deduped.append(text)
            seen.add(text)
    return deduped
