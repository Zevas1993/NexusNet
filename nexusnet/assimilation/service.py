from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow


class AssimilationControlPlane:
    CATEGORIES = {
        "durable_execution",
        "telemetry",
        "eval_gate",
        "retrieval",
        "memory",
        "runtime",
        "provider_router",
        "security",
        "protocol",
        "code_agent",
        "training",
        "operator_ux",
    }

    DEFAULT_CANDIDATES = [
        ("durable_execution", "LangGraph / Temporal / DBOS", "https://docs.langchain.com/oss/python/langgraph/overview", "workflows"),
        ("telemetry", "OpenTelemetry GenAI / OpenInference", "https://opentelemetry.io/docs/specs/semconv/gen-ai/", "telemetry"),
        ("eval_gate", "Ragas / DeepEval / promptfoo / Inspect", "https://docs.ragas.io/en/stable/", "evals"),
        ("retrieval", "GraphRAG / LightRAG / LlamaIndex / Haystack", "https://microsoft.github.io/graphrag/", "retrieval"),
        ("memory", "Letta / mem0 / Zep", "https://docs.letta.com/", "memory"),
        ("runtime", "vLLM / SGLang / TGI / TensorRT-LLM", "https://docs.vllm.ai/en/latest/", "runtime"),
        ("provider_router", "LiteLLM / Ollama / LM Studio", "https://docs.litellm.ai/docs/", "providers"),
        ("security", "OWASP / NIST / garak / NeMo Guardrails", "https://owasp.org/www-project-top-10-for-large-language-model-applications/", "product_sweep"),
        ("protocol", "MCP / A2A / AG-UI", "https://modelcontextprotocol.io/docs/getting-started/intro", "protocols"),
        ("code_agent", "OpenHands / Aider / SWE-agent / Continue", "https://github.com/OpenHands/OpenHands", "parallel_runs"),
        ("training", "TRL / Unsloth / Axolotl", "https://huggingface.co/docs/trl/index", "training"),
        ("operator_ux", "Open WebUI / LibreChat / Dify", "https://github.com/open-webui/open-webui", "ui_surface"),
    ]

    GATE_MAP = {
        "durable_execution": ["phase-9-product-ops", "gateway-policy"],
        "telemetry": ["phase-2-trace-evals", "phase-9-product-ops"],
        "eval_gate": ["phase-2-trace-evals", "phase-8-training"],
        "retrieval": ["phase-6-context-assembly", "promotion-provenance-gate"],
        "memory": ["phase-3-memory-os", "provenance-gate"],
        "runtime": ["phase-7-runtime", "runtime-certification"],
        "provider_router": ["phase-7-runtime", "gateway-policy"],
        "security": ["phase-4-security", "product-sweep-security"],
        "protocol": ["phase-4-security", "protocol-adapter-governance"],
        "code_agent": ["phase-9-product-ops", "parallel-run-gate"],
        "training": ["phase-8-training", "license-review"],
        "operator_ux": ["phase-9-product-ops", "operator-surface-truthfulness"],
    }

    SPACE_AGENT_PATTERN_LIBRARY = {
        "registered_browser_surfaces": {
            "nexusnet_target": "ui_surface.browser_surface_registry",
            "recommendation": "Add a governed browser-surface registry for operator-visible pages, inline browser widgets, focus state, and prompt-time context summaries.",
            "priority": "high",
            "governance_posture": "observe_by_default_mutation_requires_gateway",
            "product_sweep_gate_ids": ["operator-surface-truthfulness", "protocol-adapter-governance", "security-review"],
            "risk_flags": ["browser_surface_data_egress", "browser_action_spoofing", "prompt_context_inflation"],
        },
        "hierarchical_agents_skills": {
            "nexusnet_target": "tools.context_gated_skill_catalog",
            "recommendation": "Assimilate context-gated skill manifests and hierarchical AGENTS-style ownership docs into NexusNet's extension catalog and plan-review evidence.",
            "priority": "high",
            "governance_posture": "metadata_only_until_extension_certified",
            "product_sweep_gate_ids": ["extension-provenance-gate", "license-review", "operator-surface-truthfulness"],
            "risk_flags": ["instruction_shadowing", "skill_prompt_injection", "extension_conflict"],
        },
        "workspace_spaces_widgets": {
            "nexusnet_target": "ui_surface.workspace_widget_runtime",
            "recommendation": "Model operator spaces as governed workspace surfaces backed by reviewable manifests, artifact provenance, and bounded widget permissions.",
            "priority": "high",
            "governance_posture": "widget_mutation_requires_policy_grant",
            "product_sweep_gate_ids": ["operator-surface-truthfulness", "extension-provenance-gate", "security-review"],
            "risk_flags": ["user_authored_ui_code", "remote_asset_fetch", "artifact_write_surface"],
        },
        "customware_layers": {
            "nexusnet_target": "package_candidates.layered_workspace_overlay",
            "recommendation": "Adopt a firmware/group/user overlay mental model for package candidates, recipes, prompts, and operator-authored artifacts.",
            "priority": "medium",
            "governance_posture": "overlay_write_requires_owner_policy",
            "product_sweep_gate_ids": ["license-review", "provenance-gate", "operator-surface-truthfulness"],
            "risk_flags": ["layer_override_conflict", "cross_user_isolation", "quota_enforcement_required"],
        },
        "git_backed_time_travel": {
            "nexusnet_target": "memory_governance.layered_time_travel",
            "recommendation": "Extend artifact and memory governance with optional local Git-backed history, preview, rollback, and revert metadata for writable operator state.",
            "priority": "medium",
            "governance_posture": "rollback_requires_human_confirmation_and_gate",
            "product_sweep_gate_ids": ["phase-3-memory-os", "provenance-gate", "operator-surface-truthfulness"],
            "risk_flags": ["rollback_destructive_effect", "auth_file_exclusion_required", "history_privacy_review"],
        },
        "browser_local_inference": {
            "nexusnet_target": "runtime.browser_local_inference_scorecards",
            "recommendation": "Track browser-local inference runtimes such as WebGPU ONNX/Transformers/WebLLM as adaptive capability scorecards, not mandatory dependencies.",
            "priority": "medium",
            "governance_posture": "probe_first_no_model_download_without_policy",
            "product_sweep_gate_ids": ["phase-7-runtime", "runtime-certification", "security-review"],
            "risk_flags": ["large_model_download", "browser_cache_privacy", "gpu_memory_pressure"],
        },
        "plain_text_javascript_actions": {
            "nexusnet_target": "gateway.script_action_recipes",
            "recommendation": "Only assimilate the low-friction action shape as policy-reviewed script-action recipes; never allow arbitrary JavaScript execution by default.",
            "priority": "high",
            "governance_posture": "deny_by_default_script_execution",
            "product_sweep_gate_ids": ["gateway-policy", "security-review", "operator-surface-truthfulness"],
            "risk_flags": ["arbitrary_script_execution", "file_write_surface", "network_egress_surface"],
        },
    }

    SPACE_AGENT_DIRECT_REJECTIONS = [
        {
            "item": "source_code_or_vendor_assets",
            "decision": "reject_direct_adoption",
            "reason": "NexusNet assimilates architecture patterns only; source, assets, vendored runtimes, and prompts require clean-room implementation and license review.",
        },
        {
            "item": "arbitrary_plain_javascript_execution",
            "decision": "reject_direct_adoption",
            "reason": "NexusNet gateway and product-sweep policy must remain the authority for tool, script, file, network, provider, and browser mutations.",
        },
        {
            "item": "ungoverned_runtime_ui_mutation",
            "decision": "reject_direct_adoption",
            "reason": "Operator-facing UI mutation must be traceable, reversible, and linked to artifact provenance and approval state.",
        },
    ]

    def __init__(self, *, artifacts_dir: Path | str, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "assimilation-candidates"
        self.space_agent_dir = self.artifacts_dir / "space-agent-assimilation"
        self.events = events

    def ingest(
        self,
        *,
        category: str,
        source_name: str,
        source_url: str,
        license_posture: str = "requires_review",
        target_subsystem: str | None = None,
        governance_status: str = "gated",
        provenance: dict[str, Any] | None = None,
        scorecard: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if category not in self.CATEGORIES:
            raise ValueError(f"unsupported assimilation category: {category}")
        record = self._candidate(
            category=category,
            source_name=source_name,
            source_url=source_url,
            license_posture=license_posture,
            target_subsystem=target_subsystem or category,
            governance_status=governance_status,
            provenance=provenance or {"source": "operator-ingest", "ingested_at": utcnow().isoformat()},
            scorecard=scorecard or {},
        )
        self._write(record)
        if self.events:
            self.events.record(
                event_type="assimilation.candidate_ingested",
                subject=f"assimilation:{record['candidate_id']}",
                payload={
                    "category": category,
                    "governance_status": governance_status,
                    "execution_allowed": False,
                    "mutation_allowed": False,
                },
            )
        return {"status_label": "STRONG ACCEPTED DIRECTION", "candidate": record}

    def review_space_agent(
        self,
        *,
        source_url: str,
        commit_sha: str = "",
        license_posture: str = "requires_review",
        observed_patterns: list[str] | None = None,
        evidence: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        source_url = source_url.strip()
        if not source_url:
            raise ValueError("source_url is required")
        patterns = [pattern for pattern in (observed_patterns or []) if pattern]
        if not patterns:
            patterns = list(self.SPACE_AGENT_PATTERN_LIBRARY)
        recommendations = [self._space_agent_recommendation(pattern) for pattern in patterns]
        gate_ids = set(self.GATE_MAP["operator_ux"])
        risk_flags = {"clean_room_required", "metadata_only_review", "external_source_not_executed"}
        for item in recommendations:
            gate_ids.update(item["product_sweep_gate_ids"])
            risk_flags.update(item["risk_flags"])

        review_id = f"spaceagent_{self._slug((commit_sha or source_url)[0:12] or 'review')}"
        artifact_path = self.space_agent_dir / f"{review_id}.json"
        candidate = self._candidate(
            category="operator_ux",
            source_name="Space Agent",
            source_url=source_url,
            license_posture=license_posture,
            target_subsystem="ui_surface",
            governance_status="gated",
            provenance={
                "source": "space-agent-clean-room-review",
                "metadata_only": True,
                "source_commit_sha": commit_sha,
                "observed_at": utcnow().isoformat(),
                "review_id": review_id,
            },
            scorecard={
                "source_assimilated_as_pattern": True,
                "review_id": review_id,
                "observed_patterns": patterns,
                "recommended_target_count": len({item["nexusnet_target"] for item in recommendations}),
                "risk_flags": sorted(risk_flags),
            },
        )
        self._write(candidate)
        review = {
            "review_id": review_id,
            "status": "reviewed_metadata_only",
            "source": {
                "source_name": "Space Agent",
                "source_url": source_url,
                "commit_sha": commit_sha,
                "license_posture": license_posture,
                "observed_at": utcnow().isoformat(),
                "evidence": evidence or {},
            },
            "assimilation_candidate_id": candidate["candidate_id"],
            "recommended_assimilations": recommendations,
            "rejected_direct_adoptions": list(self.SPACE_AGENT_DIRECT_REJECTIONS),
            "risk_flags": sorted(risk_flags),
            "product_sweep_gate_ids": sorted(gate_ids),
            "policy_path": [
                {
                    "stage": "space-agent-clean-room-review",
                    "decision": "hold",
                    "reason": "patterns-only; no source execution or direct adoption",
                }
            ],
            "approval_path": {"decision": "not_requested", "human_approval_is_not_execution_authority": True},
            "direct_code_adoption_allowed": False,
            "copy_source_assets_prompts_allowed": False,
            "execution_allowed": False,
            "mutation_allowed": False,
            "telemetry_trace_ids": [f"trace_{review_id}"],
            "artifact_path": str(artifact_path).replace("\\", "/"),
            "created_at": utcnow().isoformat(),
        }
        self._write_space_agent_review(review)
        if self.events:
            self.events.record(
                event_type="assimilation.space_agent_reviewed",
                subject=f"assimilation:space-agent:{review_id}",
                trace_ids=review["telemetry_trace_ids"],
                payload={
                    "review_id": review_id,
                    "source_url": source_url,
                    "commit_sha": commit_sha,
                    "recommended_count": len(recommendations),
                    "execution_allowed": False,
                    "mutation_allowed": False,
                },
            )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "review": review,
            "assimilation_candidate": candidate,
        }

    def summary(self, *, limit: int = 100) -> dict[str, Any]:
        items = [*self._default_candidates(), *self._persisted_candidates()]
        items = sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)[:limit]
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "candidate_count": len(items),
            "category_counts": self._counts(items, "category"),
            "governance_status_counts": self._counts(items, "governance_status"),
            "external_execution_allowed": False,
            "remote_agent_spawning_allowed": False,
            "package_execution_allowed": False,
            "provider_registration_allowed": False,
            "promotion_requires_product_sweep": True,
            "latest_candidate": items[0] if items else None,
            "items": items,
        }

    def space_agent_summary(self, *, limit: int = 20) -> dict[str, Any]:
        items = self._space_agent_reviews(limit=limit)
        recommendations = [item for review in items for item in review.get("recommended_assimilations", [])]
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "review_count": len(items),
            "latest_review": items[0] if items else None,
            "recommended_target_counts": self._counts(recommendations, "nexusnet_target"),
            "risk_flags": sorted({flag for review in items for flag in review.get("risk_flags", [])}),
            "direct_code_adoption_allowed": False,
            "copy_source_assets_prompts_allowed": False,
            "execution_allowed": False,
            "mutation_allowed": False,
            "items": items,
        }

    def space_agent_compact_summary(self, *, limit: int = 10) -> dict[str, Any]:
        payload = self.space_agent_summary(limit=limit)
        return {
            "status_label": payload["status_label"],
            "review_count": payload["review_count"],
            "latest_review": payload["latest_review"],
            "risk_flags": payload["risk_flags"],
            "direct_code_adoption_allowed": False,
            "execution_allowed": False,
            "mutation_allowed": False,
        }

    def _default_candidates(self) -> list[dict[str, Any]]:
        return [
            self._candidate(
                category=category,
                source_name=name,
                source_url=url,
                license_posture="candidate_requires_review",
                target_subsystem=target,
                governance_status="gated",
                provenance={"source": "broad-research", "metadata_only": True},
                scorecard={"metadata_only_v1": True, "source_assimilated_as_pattern": True},
                created_at="2026-04-27T00:00:00+00:00",
            )
            for category, name, url, target in self.DEFAULT_CANDIDATES
        ]

    def _candidate(
        self,
        *,
        category: str,
        source_name: str,
        source_url: str,
        license_posture: str,
        target_subsystem: str,
        governance_status: str,
        provenance: dict[str, Any],
        scorecard: dict[str, Any],
        created_at: str | None = None,
    ) -> dict[str, Any]:
        candidate_id = f"asim_{self._slug(category)}_{self._slug(source_name)}"
        return {
            "candidate_id": candidate_id,
            "category": category,
            "source_name": source_name,
            "source_url": source_url,
            "license_posture": license_posture,
            "target_subsystem": target_subsystem,
            "governance_status": governance_status,
            "product_sweep_gate_ids": self.GATE_MAP.get(category, ["product-sweep-required"]),
            "policy_path": [{"stage": "assimilation", "decision": "hold", "reason": "metadata-only-v1"}],
            "approval_path": {"decision": "not_requested", "human_approval_is_not_execution_authority": True},
            "provenance": provenance,
            "scorecard": {
                "metadata_only_v1": True,
                "execution_allowed": False,
                "mutation_allowed": False,
                **scorecard,
            },
            "implementation_readiness": {
                "status": "candidate",
                "external_dependency_required": False,
                "requires_gateway_grant": True,
                "requires_product_sweep_pass": True,
            },
            "artifacts": [str(self.output_dir / f"{candidate_id}.json").replace("\\", "/")],
            "created_at": created_at or utcnow().isoformat(),
        }

    def _persisted_candidates(self) -> list[dict[str, Any]]:
        if not self.output_dir.exists():
            return []
        items = []
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
        return items

    def _write(self, record: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{record['candidate_id']}.json"
        record["artifacts"] = [str(path).replace("\\", "/")]
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _write_space_agent_review(self, record: dict[str, Any]) -> None:
        self.space_agent_dir.mkdir(parents=True, exist_ok=True)
        path = self.space_agent_dir / f"{record['review_id']}.json"
        record["artifact_path"] = str(path).replace("\\", "/")
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _space_agent_reviews(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.space_agent_dir.exists():
            return []
        items = []
        for path in sorted(self.space_agent_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(items) >= limit:
                break
        return items

    def _space_agent_recommendation(self, pattern: str) -> dict[str, Any]:
        item = self.SPACE_AGENT_PATTERN_LIBRARY.get(pattern)
        if item is None:
            item = {
                "nexusnet_target": "assimilation.unclassified_review_queue",
                "recommendation": "Hold unclassified Space Agent pattern for operator review before mapping it to a NexusNet subsystem.",
                "priority": "low",
                "governance_posture": "manual_review_required",
                "product_sweep_gate_ids": ["license-review", "security-review"],
                "risk_flags": ["unclassified_pattern"],
            }
        return {
            "pattern": pattern,
            "nexusnet_target": item["nexusnet_target"],
            "recommendation": item["recommendation"],
            "priority": item["priority"],
            "governance_posture": item["governance_posture"],
            "product_sweep_gate_ids": list(item["product_sweep_gate_ids"]),
            "risk_flags": list(item["risk_flags"]),
            "clean_room_required": True,
            "external_dependency_required": False,
            "execution_allowed": False,
            "mutation_allowed": False,
        }

    def _counts(self, items: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = str(item.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _slug(self, value: Any) -> str:
        slug = "".join(ch if ch.isalnum() else "-" for ch in str(value).lower()).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug or "unknown"
