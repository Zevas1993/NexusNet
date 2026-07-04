from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class AutonomousGrowthControlPlane:
    """Governed metadata lane for NexusNet self-growth assimilation targets.

    V1 deliberately records manifests, scorecards, eval plans, optimizer shadow
    proposals, and evidence records without starting sandboxes, installing
    packages, registering providers, mutating memory, or changing model packs.
    """

    WAVE_TARGETS: dict[str, list[dict[str, Any]]] = {
        "wave_1_execution_security": [
            {
                "target_id": "sandbox_manifest_execution",
                "source_targets": ["OpenAI Agents SDK Sandbox", "Daytona", "E2B"],
                "target_subsystem": "parallel_runs",
                "capability_family": "code_agent",
                "required_capabilities": ["sandbox_workspace_execution", "file_write", "autonomous_agent_execution"],
                "product_sweep_gate_ids": ["execution-authority", "sandbox-policy", "product-sweep-security"],
                "eval_suite_ids": ["workflow_completion", "prompt_security_red_team"],
            },
            {
                "target_id": "deterministic_tool_boundary_security",
                "source_targets": ["ClawGuard", "AgentDojo", "MCP OAuth resource binding"],
                "target_subsystem": "gateway",
                "capability_family": "security",
                "required_capabilities": ["deterministic_tool_boundary", "network_write", "file_write"],
                "product_sweep_gate_ids": ["gateway-policy", "deterministic-tool-boundary", "product-sweep-security"],
                "eval_suite_ids": ["tool_call_accuracy", "prompt_security_red_team"],
            },
            {
                "target_id": "protocol_trust_registry",
                "source_targets": ["MCP Registry/Auth", "A2A", "AG-UI"],
                "target_subsystem": "protocols",
                "capability_family": "protocol_tooling",
                "required_capabilities": ["protocol_trust_registration", "provider_registration"],
                "product_sweep_gate_ids": ["protocol-trust-gate", "provider-registration-gate", "product-sweep-security"],
                "eval_suite_ids": ["tool_call_accuracy", "prompt_security_red_team"],
            },
        ],
        "wave_2_measurement": [
            {
                "target_id": "otel_openinference_trace_export",
                "source_targets": ["OpenTelemetry GenAI", "OpenInference", "Phoenix"],
                "target_subsystem": "telemetry",
                "capability_family": "telemetry",
                "required_capabilities": ["telemetry_export", "network_write"],
                "product_sweep_gate_ids": ["telemetry-redaction-gate", "trace-export-gate"],
                "eval_suite_ids": ["regression_behavior", "prompt_security_red_team"],
            },
            {
                "target_id": "raw_trace_optimizer_shadow",
                "source_targets": ["DSPy GEPA", "TextGrad", "Agent Lightning", "Meta Harness"],
                "target_subsystem": "harness_engineering",
                "capability_family": "self_improvement",
                "required_capabilities": ["shadow_optimizer_run", "harness_optimization", "model_growth_cycle"],
                "product_sweep_gate_ids": ["raw-trace-privacy-gate", "harness-optimization-gate", "promotion-provenance-gate"],
                "eval_suite_ids": ["harness_ablation", "workflow_completion", "regression_behavior"],
            },
            {
                "target_id": "paired_eval_skill_harness_utility",
                "source_targets": ["Pydantic Evals", "Inspect", "SWE-Skills-Bench"],
                "target_subsystem": "evals",
                "capability_family": "eval",
                "required_capabilities": ["paired_eval_run"],
                "product_sweep_gate_ids": ["eval-gate", "promotion-provenance-gate"],
                "eval_suite_ids": ["paired_skill_utility", "workflow_completion", "regression_behavior"],
            },
        ],
        "wave_3_capability_expansion": [
            {
                "target_id": "edge_runtime_pack_certification",
                "source_targets": ["ONNX Runtime Execution Providers", "ExecuTorch", "LiteRT", "MLC LLM"],
                "target_subsystem": "runtime",
                "capability_family": "inference",
                "required_capabilities": ["runtime_pack_certification", "model_download"],
                "product_sweep_gate_ids": ["phase-7-runtime", "edge-runtime-certification", "license-review"],
                "eval_suite_ids": ["runtime_quality", "cost_energy"],
            },
            {
                "target_id": "serving_gateway_performance",
                "source_targets": ["vLLM prefix caching", "SGLang model gateway", "TGI", "TensorRT-LLM"],
                "target_subsystem": "runtime",
                "capability_family": "provider_fallback",
                "required_capabilities": ["serving_gateway_probe", "provider_registration", "cloud_fallback"],
                "product_sweep_gate_ids": ["phase-7-runtime", "provider-router-gate", "cost-budget-gate"],
                "eval_suite_ids": ["runtime_quality", "tool_call_accuracy"],
            },
            {
                "target_id": "stateful_memory_hierarchy",
                "source_targets": ["Letta", "Zep", "Graphiti"],
                "target_subsystem": "memory",
                "capability_family": "memory",
                "required_capabilities": ["memory_hierarchy_mutation", "file_write"],
                "product_sweep_gate_ids": ["memory-governance-gate", "memory-provenance-gate", "product-sweep-security"],
                "eval_suite_ids": ["regression_behavior", "rag_quality"],
            },
            {
                "target_id": "citation_grounded_research_scout",
                "source_targets": ["GraphRAG DRIFT", "LightRAG", "PaperQA2", "Deep Research API"],
                "target_subsystem": "research_scout",
                "capability_family": "research",
                "required_capabilities": ["citation_research_ingestion", "network_write"],
                "product_sweep_gate_ids": ["research-provenance-gate", "license-review", "telemetry-redaction-gate"],
                "eval_suite_ids": ["rag_quality", "citation_grounding", "prompt_security_red_team"],
            },
        ],
    }

    RECORD_DIRS = {
        "activation": "activations",
        "sandbox_manifest": "sandbox-manifests",
        "security_boundary": "security-boundaries",
        "telemetry_export_plan": "telemetry-export-plans",
        "optimizer_shadow_run": "optimizer-shadow-runs",
        "paired_eval": "paired-evals",
        "runtime_pack_certification": "runtime-pack-certifications",
        "serving_scorecard": "serving-scorecards",
        "protocol_trust": "protocol-trust",
        "memory_hierarchy": "memory-hierarchy",
        "research_evidence": "research-evidence",
    }

    def __init__(
        self,
        *,
        artifacts_dir: Path | str,
        events: Any | None = None,
        execution_authority: Any | None = None,
        assimilation: Any | None = None,
        harness_engineering: Any | None = None,
        eval_suites: Any | None = None,
        runtime_scorecards: Any | None = None,
        memory_governance: Any | None = None,
        research_scout: Any | None = None,
    ):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "autonomous-growth"
        self.events = events
        self.execution_authority = execution_authority
        self.assimilation = assimilation
        self.harness_engineering = harness_engineering
        self.eval_suites = eval_suites
        self.runtime_scorecards = runtime_scorecards
        self.memory_governance = memory_governance
        self.research_scout = research_scout

    def summary(self, *, limit: int = 100) -> dict[str, Any]:
        records = self._records(limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "blueprint_target_count": len(self._blueprints()),
            "blueprint_wave_counts": self._blueprint_wave_counts(),
            "target_ids": sorted(self._blueprints()),
            "record_count": len(records),
            "wave_counts": self._counts(records, "wave_id"),
            "target_counts": self._counts(records, "target_id"),
            "record_type_counts": self._counts(records, "record_type"),
            "status_counts": self._counts(records, "status"),
            "execution_allowed": False,
            "mutation_allowed": False,
            "deny_by_default": True,
            "latest_record": records[0] if records else None,
            "items": records,
        }

    def compact_summary(self, *, limit: int = 50) -> dict[str, Any]:
        payload = self.summary(limit=limit)
        return {
            "status_label": payload["status_label"],
            "blueprint_target_count": payload["blueprint_target_count"],
            "record_count": payload["record_count"],
            "wave_counts": payload["wave_counts"],
            "target_counts": payload["target_counts"],
            "status_counts": payload["status_counts"],
            "execution_allowed": False,
            "mutation_allowed": False,
            "deny_by_default": True,
            "latest_record": payload["latest_record"],
        }

    def activate(self, *, wave_ids: list[str] | None = None, operator_goal: str = "") -> dict[str, Any]:
        selected_wave_ids = [str(item) for item in (wave_ids or list(self.WAVE_TARGETS))]
        records = []
        for wave_id in selected_wave_ids:
            if wave_id not in self.WAVE_TARGETS:
                raise ValueError(f"unsupported growth wave: {wave_id}")
            for target in self.WAVE_TARGETS[wave_id]:
                record = self._base_record(
                    record_type="activation",
                    target_id=target["target_id"],
                    status="activated_metadata_only",
                    linked_trace_ids=None,
                )
                record["operator_goal"] = operator_goal
                record["activation"] = {
                    "wave_id": wave_id,
                    "target_ready_for_validation": True,
                    "execution_enabled": False,
                    "mutation_enabled": False,
                    "research_basis": target["source_targets"],
                }
                self._finalize(record, "activation", "autonomous_growth.target_activated")
                records.append(record)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "status": "activated_metadata_only",
            "target_count": len(records),
            "target_ids": sorted(record["target_id"] for record in records),
            "wave_counts": self._counts(records, "wave_id"),
            "records": records,
            "execution_allowed": False,
            "mutation_allowed": False,
        }

    def record_sandbox_manifest(
        self,
        *,
        workspace_ref: str,
        manifest: dict[str, Any],
        sandbox_providers: list[str] | None = None,
        requested_capabilities: list[str] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._base_record(
            record_type="sandbox_manifest",
            target_id="sandbox_manifest_execution",
            status="sandbox_manifest_recorded_metadata_only",
            linked_trace_ids=linked_trace_ids,
        )
        record["workspace_ref"] = workspace_ref
        record["sandbox_providers"] = [
            {"provider": str(item), "execution_allowed": False, "registration_allowed": False}
            for item in (sandbox_providers or [])
        ]
        record["requested_capabilities"] = [str(item) for item in (requested_capabilities or [])]
        record["manifest"] = {
            "portable_workspace_contract": True,
            "absolute_paths_allowed": False,
            "path_escape_allowed": False,
            "root": str(manifest.get("root") or "workspace"),
            "files": [str(item) for item in (manifest.get("files") or [])],
            "dirs": [str(item) for item in (manifest.get("dirs") or [])],
            "git_repos": [dict(item) for item in (manifest.get("git_repos") or [])],
            "redacted_env": self._redact_env(dict(manifest.get("env") or {})),
            "provider_execution_allowed": False,
            "hook_write_allowed": False,
        }
        self._finalize(record, "sandbox_manifest", "autonomous_growth.sandbox_manifest_recorded")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def derive_security_boundary(
        self,
        *,
        objective: str,
        tool_requests: list[dict[str, Any]] | None = None,
        content_channels: list[str] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._base_record(
            record_type="security_boundary",
            target_id="deterministic_tool_boundary_security",
            status="security_boundary_derived_metadata_only",
            linked_trace_ids=linked_trace_ids,
        )
        record["objective"] = objective
        record["attack_channels"] = sorted({str(item) for item in (content_channels or [])})
        record["boundary_policy"] = {
            "deterministic_tool_boundary": True,
            "default_decision": "deny",
            "allowlist_required": True,
            "content_instruction_authority": "untrusted",
            "mutating_tool_requires_execution_authority": True,
        }
        record["tool_decisions"] = [self._tool_decision(dict(item)) for item in (tool_requests or [])]
        self._finalize(record, "security_boundary", "autonomous_growth.security_boundary_derived")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def plan_trace_export(
        self,
        *,
        trace_ids: list[str],
        destination: str,
        formats: list[str],
        redaction_policy: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._base_record(
            record_type="telemetry_export_plan",
            target_id="otel_openinference_trace_export",
            status="trace_export_planned_metadata_only",
            linked_trace_ids=linked_trace_ids or trace_ids,
        )
        normalized_formats = [str(item) for item in formats]
        record["export_plan"] = {
            "trace_ids": [str(item) for item in trace_ids],
            "destination": destination,
            "formats": normalized_formats,
            "otel_genai_shape": "otel_genai" in normalized_formats,
            "openinference_shape": "openinference" in normalized_formats,
            "network_write_allowed": False,
            "export_execution_allowed": False,
        }
        record["redaction_policy"] = {
            "mode": "metadata_plus_refs",
            "raw_content_export": False,
            **(redaction_policy or {}),
        }
        self._finalize(record, "telemetry_export_plan", "autonomous_growth.telemetry_export_planned")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def propose_shadow_optimizer(
        self,
        *,
        target_subsystem: str,
        raw_trace_ids: list[str],
        summary_trace_ids: list[str] | None = None,
        candidate_change: str,
        transfer_models: list[str] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._base_record(
            record_type="optimizer_shadow_run",
            target_id="raw_trace_optimizer_shadow",
            status="optimizer_shadow_proposed_metadata_only",
            linked_trace_ids=linked_trace_ids or raw_trace_ids,
        )
        record["target_subsystem"] = target_subsystem
        record["optimizer_loop"] = {
            "raw_traces_required": True,
            "raw_trace_ids": [str(item) for item in raw_trace_ids],
            "summary_trace_ids": [str(item) for item in (summary_trace_ids or [])],
            "summaries_alone_sufficient": False,
            "candidate_change": candidate_change,
            "transfer_models": [str(item) for item in (transfer_models or [])],
            "shadow_only": True,
            "promotion_requires_product_sweep": True,
            "model_weight_mutation_allowed": False,
        }
        self._finalize(record, "optimizer_shadow_run", "autonomous_growth.optimizer_shadow_proposed")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def record_paired_eval(
        self,
        *,
        subject: str,
        baseline: dict[str, Any],
        variant: dict[str, Any],
        acceptance_criteria: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        criteria = acceptance_criteria or {}
        pass_delta = round(self._float(variant.get("pass_rate")) - self._float(baseline.get("pass_rate")), 6)
        token_delta_ratio = self._delta_ratio(self._float(baseline.get("tokens")), self._float(variant.get("tokens")))
        latency_delta_ratio = self._delta_ratio(self._float(baseline.get("latency_ms")), self._float(variant.get("latency_ms")))
        min_pass_delta = self._float(criteria.get("min_pass_delta"))
        max_token_delta_ratio = self._float(criteria.get("max_token_delta_ratio"))
        decision = (
            "promote_to_validation"
            if pass_delta >= min_pass_delta and token_delta_ratio <= max_token_delta_ratio
            else "hold_for_more_evidence"
        )
        record = self._base_record(
            record_type="paired_eval",
            target_id="paired_eval_skill_harness_utility",
            status="paired_eval_recorded_metadata_only",
            linked_trace_ids=linked_trace_ids,
        )
        record["paired_eval"] = {
            "subject": subject,
            "baseline": baseline,
            "variant": variant,
            "acceptance_criteria": criteria,
            "pass_delta": pass_delta,
            "token_delta_ratio": token_delta_ratio,
            "latency_delta_ratio": latency_delta_ratio,
            "decision": decision,
            "promotion_requires_product_sweep": True,
        }
        record["promotion_allowed"] = False
        self._finalize(record, "paired_eval", "autonomous_growth.paired_eval_recorded")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def certify_runtime_pack(
        self,
        *,
        runtime_id: str,
        hardware_tier: str,
        model_formats: list[str] | None = None,
        accelerators: list[str] | None = None,
        measurements: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._base_record(
            record_type="runtime_pack_certification",
            target_id="edge_runtime_pack_certification",
            status="runtime_pack_certification_recorded_metadata_only",
            linked_trace_ids=linked_trace_ids,
        )
        record["certification"] = {
            "runtime_id": runtime_id,
            "hardware_tier": hardware_tier,
            "model_formats": [str(item) for item in (model_formats or [])],
            "accelerators": [str(item) for item in (accelerators or [])],
            "measurements": measurements or {},
            "status": "certification_candidate",
            "external_server_started": False,
            "model_download_allowed": False,
        }
        self._finalize(record, "runtime_pack_certification", "autonomous_growth.runtime_pack_certification_recorded")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def record_serving_scorecard(
        self,
        *,
        provider_id: str,
        features: dict[str, Any] | None = None,
        measurements: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        feature_payload = features or {}
        record = self._base_record(
            record_type="serving_scorecard",
            target_id="serving_gateway_performance",
            status="serving_scorecard_recorded_metadata_only",
            linked_trace_ids=linked_trace_ids,
        )
        record["serving_scorecard"] = {
            "provider_id": provider_id,
            "features": feature_payload,
            "measurements": measurements or {},
            "prefix_cache_probe": {
                "state": "supported_metadata" if feature_payload.get("prefix_cache") else "unknown_or_unsupported",
                "live_probe_executed": False,
            },
            "structured_output_support": bool(feature_payload.get("structured_outputs", False)),
            "tool_calling_support": bool(feature_payload.get("tool_calling", False)),
            "routing_mode": "governed_local_or_tier5",
            "external_server_started": False,
            "provider_registration_allowed": False,
            "cloud_fallback_allowed_only_as_tier5": True,
        }
        self._finalize(record, "serving_scorecard", "autonomous_growth.serving_scorecard_recorded")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def record_protocol_trust(
        self,
        *,
        protocol_id: str,
        server_ref: str,
        auth: dict[str, Any] | None = None,
        capability_manifest: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        auth_payload = auth or {}
        manifest = capability_manifest or {}
        record = self._base_record(
            record_type="protocol_trust",
            target_id="protocol_trust_registry",
            status="protocol_trust_recorded_metadata_only",
            linked_trace_ids=linked_trace_ids,
        )
        record["protocol_id"] = protocol_id
        record["server_ref"] = server_ref
        record["trust_requirements"] = {
            "oauth_2_1": bool(auth_payload.get("oauth_2_1", False)),
            "resource_metadata": bool(auth_payload.get("resource_metadata", False)),
            "audience_bound_tokens": bool(auth_payload.get("audience_bound_tokens", False)),
            "pkce": bool(auth_payload.get("pkce", False)),
            "token_passthrough_allowed": bool(auth_payload.get("token_passthrough", False)),
            "consent_required": True,
        }
        record["capability_manifest"] = {
            "tools": [str(item) for item in (manifest.get("tools") or [])],
            "mutating_tools": [str(item) for item in (manifest.get("mutating_tools") or [])],
            "streaming": bool(manifest.get("streaming", False)),
            "filesystem_posture": manifest.get("filesystem_posture", "unknown"),
            "network_posture": manifest.get("network_posture", "unknown"),
        }
        record["risk_posture"] = {
            "provider_registration_allowed": False,
            "external_protocol_execution_allowed": False,
            "mutation_allowed": False,
            "data_egress_risk": "requires_review",
            "sandbox_recommendation": "deny_mutation_until_scoped_lease",
        }
        self._finalize(record, "protocol_trust", "autonomous_growth.protocol_trust_recorded")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def record_memory_hierarchy(
        self,
        *,
        agent_ref: str,
        core_blocks: list[dict[str, Any]] | None = None,
        archival_refs: list[str] | None = None,
        shared_blocks: list[dict[str, Any]] | None = None,
        contradictions: list[dict[str, Any]] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._base_record(
            record_type="memory_hierarchy",
            target_id="stateful_memory_hierarchy",
            status="memory_hierarchy_recorded_metadata_only",
            linked_trace_ids=linked_trace_ids,
        )
        record["agent_ref"] = agent_ref
        record["memory_hierarchy"] = {
            "core_memory": {
                "block_count": len(core_blocks or []),
                "blocks": [dict(item) for item in (core_blocks or [])],
                "mutation_allowed": False,
            },
            "archival_memory": {
                "ref_count": len(archival_refs or []),
                "refs": [str(item) for item in (archival_refs or [])],
            },
            "shared_memory": {
                "block_count": len(shared_blocks or []),
                "blocks": [dict(item) for item in (shared_blocks or [])],
                "mutation_allowed": False,
                "approval_required": True,
            },
            "contradiction_count": len(contradictions or []),
            "contradictions": [dict(item) for item in (contradictions or [])],
            "provenance_diff_required": True,
        }
        self._finalize(record, "memory_hierarchy", "autonomous_growth.memory_hierarchy_recorded")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def ingest_research_evidence(
        self,
        *,
        source_name: str,
        source_url: str,
        claim: str,
        citations: list[dict[str, Any]] | None = None,
        credibility: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._base_record(
            record_type="research_evidence",
            target_id="citation_grounded_research_scout",
            status="research_evidence_ingested_metadata_only",
            linked_trace_ids=linked_trace_ids,
        )
        citation_items = [dict(item) for item in (citations or [])]
        record["research_evidence"] = {
            "source_name": source_name,
            "source_url": source_url,
            "claim": claim,
            "citations": citation_items,
            "citation_count": len(citation_items),
            "credibility": credibility or {},
            "source_metadata_required": True,
            "candidate_ingestion_status": "metadata_only",
            "dependency_install_allowed": False,
            "network_fetch_allowed_without_policy": False,
        }
        self._finalize(record, "research_evidence", "autonomous_growth.research_evidence_ingested")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def _base_record(
        self,
        *,
        record_type: str,
        target_id: str,
        status: str,
        linked_trace_ids: list[str] | None,
    ) -> dict[str, Any]:
        blueprint = self._blueprint(target_id)
        record_id = new_id("growth")
        trace_ids = list(linked_trace_ids or []) or [f"trace_{record_id}"]
        return {
            "record_id": record_id,
            "record_type": record_type,
            "target_id": target_id,
            "wave_id": blueprint["wave_id"],
            "status": status,
            "source_targets": list(blueprint["source_targets"]),
            "target_subsystem": blueprint["target_subsystem"],
            "capability_family": blueprint["capability_family"],
            "policy_path": [
                {
                    "stage": "autonomous-growth-control-plane",
                    "decision": "hold",
                    "reason": "research targets are metadata-only until eval, product-sweep, gateway, and execution-authority gates pass",
                }
            ],
            "approval_path": {"decision": "not_requested", "human_approval_is_not_execution_authority": True},
            "product_sweep_gate_ids": list(blueprint["product_sweep_gate_ids"]),
            "eval_suite_ids": list(blueprint["eval_suite_ids"]),
            "telemetry_trace_ids": trace_ids,
            "execution_authority": self._execution_authority(blueprint["required_capabilities"]),
            "provenance": {
                "service": "autonomous-growth-control-plane",
                "research_assimilation": True,
                "metadata_only": True,
                "created_at": utcnow().isoformat(),
            },
            "artifacts": [],
            "execution_allowed": False,
            "mutation_allowed": False,
            "created_at": utcnow().isoformat(),
        }

    def _execution_authority(self, capabilities: list[str]) -> dict[str, Any]:
        return {
            "required": True,
            "service": "execution_authority",
            "lease_endpoint": "/ops/brain/execution-authority/leases/request",
            "required_capabilities": [str(item) for item in capabilities],
            "execution_allowed": False,
            "mutation_allowed": False,
            "reason": "Growth-control records can propose validation only; execution and mutation require a scoped expiring lease plus gateway and product-sweep authority.",
        }

    def _redact_env(self, env: dict[str, Any]) -> dict[str, str]:
        redacted = {}
        sensitive_markers = ("SECRET", "TOKEN", "KEY", "PASSWORD", "CREDENTIAL")
        for key, value in env.items():
            normalized_key = str(key)
            if any(marker in normalized_key.upper() for marker in sensitive_markers):
                redacted[normalized_key] = "<redacted>"
            else:
                redacted[normalized_key] = str(value)
        return redacted

    def _tool_decision(self, request: dict[str, Any]) -> dict[str, Any]:
        action = str(request.get("action") or "").lower()
        tool = str(request.get("tool") or "unknown")
        dangerous_markers = [
            "install",
            "post",
            "write",
            "delete",
            "push",
            "merge",
            "deploy",
            "register",
            "download",
            "exec",
            "shell",
        ]
        read_only = action in {"read", "list", "inspect", "query"}
        decision = "allow_metadata_only" if read_only and tool not in {"shell", "network"} else "deny"
        if any(marker in action for marker in dangerous_markers):
            decision = "deny"
        return {
            "tool": tool,
            "action": request.get("action"),
            "decision": decision,
            "execution_allowed": False,
            "mutation_allowed": False,
            "reason": "read-only metadata action" if decision == "allow_metadata_only" else "requires allowlist and execution authority lease",
        }

    def _finalize(self, record: dict[str, Any], record_dir_key: str, event_type: str) -> None:
        directory = self.output_dir / self.RECORD_DIRS[record_dir_key]
        path = directory / f"{record['record_id']}.json"
        record["artifact_path"] = str(path)
        record["artifacts"] = [str(path)]
        self._write(record, path)
        self._event(event_type, record)

    def _event(self, event_type: str, record: dict[str, Any]) -> None:
        if not self.events:
            return
        self.events.record(
            event_type=event_type,
            subject=f"autonomous_growth:{record['record_id']}",
            trace_ids=record.get("telemetry_trace_ids") or [],
            payload={
                "record_id": record["record_id"],
                "record_type": record["record_type"],
                "target_id": record["target_id"],
                "wave_id": record["wave_id"],
                "status": record["status"],
                "decision": "hold",
                "execution_allowed": False,
                "mutation_allowed": False,
                "artifact_path": record.get("artifact_path"),
            },
        )

    def _records(self, *, limit: int) -> list[dict[str, Any]]:
        records = []
        if not self.output_dir.exists():
            return []
        for directory in self.RECORD_DIRS.values():
            path = self.output_dir / directory
            if not path.exists():
                continue
            for item in path.glob("growth_*.json"):
                try:
                    records.append(json.loads(item.read_text(encoding="utf-8")))
                except (OSError, json.JSONDecodeError):
                    continue
        records.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        return records[:limit]

    def _write(self, payload: dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _blueprints(self) -> dict[str, dict[str, Any]]:
        blueprints: dict[str, dict[str, Any]] = {}
        for wave_id, targets in self.WAVE_TARGETS.items():
            for target in targets:
                blueprints[target["target_id"]] = {**target, "wave_id": wave_id}
        return blueprints

    def _blueprint(self, target_id: str) -> dict[str, Any]:
        blueprints = self._blueprints()
        if target_id not in blueprints:
            raise ValueError(f"unsupported growth target: {target_id}")
        return blueprints[target_id]

    def _blueprint_wave_counts(self) -> dict[str, int]:
        return {wave_id: len(targets) for wave_id, targets in self.WAVE_TARGETS.items()}

    def _counts(self, records: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in records:
            value = str(record.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _float(self, value: Any) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def _delta_ratio(self, baseline: float, variant: float) -> float:
        if baseline <= 0:
            return 0.0
        return round((variant - baseline) / baseline, 6)
