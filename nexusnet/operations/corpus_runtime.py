from __future__ import annotations

import hashlib
import importlib
import json
import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


_CANON_EXCLUSIONS = {
    "109-human-brain-atlas-connectome-ladder-spec": (
        "research-only anatomical reference; Canon forbids treating an atlas as an executable brain"
    ),
    "110-synapse-connectome-simulation-ladder-spec": (
        "research-only simulation reference; Canon forbids claiming synapse simulation as NexusBrain"
    ),
    "111-whole-brain-emulation-boundary-spec": (
        "explicit Canon boundary against whole-brain-emulation and consciousness claims"
    ),
    "112-organoid-intelligence-ethics-spec": (
        "ethics boundary and governance input; wet-lab or organoid execution is outside NexusNet scope"
    ),
}


@dataclass(frozen=True)
class NativeCluster:
    cluster_id: int
    native_output: str
    implementation_refs: tuple[str, ...]
    verified_capabilities: tuple[str, ...]
    matcher: re.Pattern[str]


def _cluster(
    cluster_id: int,
    native_output: str,
    refs: Iterable[str],
    capabilities: Iterable[str],
    pattern: str,
) -> NativeCluster:
    return NativeCluster(
        cluster_id=cluster_id,
        native_output=native_output,
        implementation_refs=tuple(refs),
        verified_capabilities=tuple(capabilities),
        matcher=re.compile(pattern, re.IGNORECASE),
    )


_CLUSTERS = (
    _cluster(
        1,
        "NexusNet Workflow Graph Studio",
        (
            "nexusnet.workflows.service:WorkflowCatalogService.execute",
            "nexusnet.workflows.execution:TypedWorkflowExecutor.execute",
        ),
        ("typed-dag", "cycle-rejection", "topological-execution-plan", "run-receipt", "capability-enforced-node-execution"),
        r"workflow|parallel-tool-dag|model-checking",
    ),
    _cluster(
        2,
        "NexusNet SkillOps And Protocol Fabric",
        (
            "nexusnet.operations.skill_system_executor:SkillSystemExecutor.execute",
            "nexus.tools.registry:ToolRegistry",
        ),
        ("composable-skills", "validated-handoffs", "protocol-surface", "tool-metadata"),
        r"mcp|protocol|tool-calling|skill|plugin|starlark|cue-constraint|capability-rpc|grammar-constrained",
    ),
    _cluster(
        3,
        "Hive Agent Workbench",
        ("nexusnet.agents.sandbox_factory:SandboxAgentFactory.start",),
        ("dependency-aware-agent-plan", "sandbox-boundary", "parallel-ready-work", "agent-receipt"),
        r"agentfloor|agentprocess|agent-race|agent-core|terminal-bench|androidworld|browsergym|osworld|swe-|computer-use|coworker|customer-reliability|professional-faults|commercial-coding|coordination|productivity-agent|durable-agent|enterprise-query|deep-research|tars-computer",
    ),
    _cluster(
        4,
        "NexusNet Runtime Ladder And Model Passport Registry",
        (
            "nexus.runtimes.registry:RuntimeRegistry",
            "nexusnet.runtime.evolutionary_inference.system:EvolutionaryInferenceSystem",
            "nexusnet.runtime.advanced_inference:GrammarConstrainedDecoder.select",
            "nexusnet.runtime.advanced_inference:LearnedCascadeRouter.route",
            "nexusnet.runtime.advanced_inference:SpeculativeDecoder.decode",
            "nexusnet.runtime.advanced_inference:VerifiedSemanticCache.get",
        ),
        ("hardware-fit", "vram-offload-plan", "runtime-ranking", "degradation-boundary", "grammar-constrained-decoding", "learned-cascade", "speculative-decoding", "verified-semantic-cache"),
        r"runtime|kv-cache|context-compression|gateway-budget|decoder|reasoning-effort|speculative|model-cascade|semantic-cache|private-compute|hardware-rights|neuromorphic|microcircuit|liquid-dynamical",
    ),
    _cluster(
        5,
        "NexusNet Knowledge Forge And Agent-Native Memory OS",
        (
            "nexusnet.knowledge.compiler:KnowledgeArtifactCompiler.query",
            "nexusnet.memory.operating_system:MemoryOperatingSystem.store",
            "nexusnet.memory.evolution:MemoryEvolutionRegistry.propose",
        ),
        ("source-grounded-memory", "retrieval", "privacy-filter", "forgetting-and-archive", "MemoryEvolutionPassport"),
        r"belief-revision|document-certification|memory|knowledge|personal-context|rag-|graphrag|context-playbook|crdt-state|spatial-kac|semantic-pointer|research-engineering",
    ),
    _cluster(
        6,
        "EvalsAO Evidence Spine",
        (
            "nexusnet.evals.suites:EvalSuiteService.run",
            "nexusnet.evals.assimilation_runtime:DeterministicFailureFoundry.run",
            "nexusnet.evals.assimilation_runtime:RuntimeMonitorSynthesizer.compile",
            "nexusnet.evals.assimilation_runtime:BenchmarkHarnessFederation.run_suite",
        ),
        ("threshold-evaluation", "failure-examples", "trace-linkage", "promotion-gate", "deterministic-failure-foundry", "runtime-monitor-synthesis", "benchmark-adapter-federation"),
        r"eval|bench|verification|verifier|observability|interpretability|assurance-case|evidence-layer|failure-foundry|monitor-synthesis|synthetic-truth|property-based|chaos|reflective-text",
    ),
    _cluster(
        7,
        "Authority And Isolation Fabric",
        (
            "nexusnet.execution_authority.service:ExecutionAuthorityService.evaluate",
            "nexusnet.authority.spine:AuthorityIntegritySpine.issue_grant",
            "nexusnet.authority.spine:AuthorityIntegritySpine.observe_effect",
            "nexusnet.security.assimilation_runtime:ObjectCapabilityRPCFabric.invoke",
            "nexusnet.security.assimilation_runtime:IsolationAndSupplyChainRuntime.probe_native_isolation",
        ),
        ("deny-by-default", "scoped-authority", "evidence-gate", "rollback-gate", "signed-capability-token", "observed-effect-receipt", "reversible-transaction", "object-capability-rpc", "taint-flow", "signed-update-root", "reproducible-build", "native-isolation-probes"),
        r"security|trust|authority|guard|red-team|owasp|policy|identity|delegation|sandbox|privacy|capability|hermetic|effect-typed|wasm|confidential|federated|syscall|authz|secure-update|proof-carrying|biscuit|scitt|zkvm|crypto-lane|landlock|seccomp|credential-passport|taint|isolation-kernel|commerce-authority",
    ),
    _cluster(
        8,
        "Recursive Dreaming And Imagination Foundry",
        (
            "nexusnet.developmental.kernel:DevelopmentalCortexKernel.assess",
            "nexusnet.developmental.advanced:AdvancedDevelopmentalRuntime.assess",
        ),
        ("candidate-only-imagination", "replay", "causal-intervention", "promotion-tribunal"),
        r"active-inference|hippocampal|morphogenesis|developmental|lullian|symbolic-change|reference-frame|world-model|self-model|causal-representation|gflownet|intrinsic-motivation|neural-cellular|autopoietic|open-ended-self|darwin-godel|alphaevolve|imagination|growth-engine",
    ),
    _cluster(
        9,
        "Teacher Council And Expert Birth Registry",
        ("nexusnet.teachers.registry:TeacherRegistry.resolve_for_task",),
        ("teacher-ranking", "rights-check", "hardware-fit", "multi-teacher-disagreement"),
        r"small-model-training|teacher|model-training",
    ),
    _cluster(
        10,
        "Expert Pack Radar And Domain Curriculum Forge",
        (
            "nexusnet.experts.ontology:OpenWorldExpertOntology",
            "nexusnet.evals.high_risk_domains:HighRiskDomainEvaluator.evaluate",
        ),
        ("domain-pack", "risk-policy", "eval-set", "retention-review", "high-risk-escalation"),
        r"domain-expert|occubench|enterpriseops|data-agent|finance|medical|legal|robotics|professional",
    ),
    _cluster(
        11,
        "NexusNet Control Panel And Companion",
        ("nexusnet.visuals.layout:NexusVisualizerService.state",),
        ("sanitized-live-state", "replay-drilldown", "status-labels", "operator-controls"),
        r"agent-ui|operator-shell|self-updating-surface|jarvis|space-agent|control-panel|companion",
    ),
    _cluster(
        12,
        "NexusNet Operational Spine",
        (
            "nexusnet.operations.change_passport:OperationalChangeRegistry.create",
            "nexusnet.operations.spine:OperationalSpineService.create_recovery_snapshot",
        ),
        ("change-passport", "feature-flag", "replay-snapshot", "rollback-lifecycle", "worktree-registry", "release-channels", "scheduler-monitor", "disaster-recovery"),
        r"research-lifecycle|provenance|supply-chain|data-model-lineage|event-sourced|feature-flag|patch-transaction|update-trust|replay-snapshot|rebuilder|flight-software|trusted-time|digital-twin|content-credential|workstream|orchestration",
    ),
    _cluster(
        13,
        "NexusGraph Intelligence Fabric",
        (
            "nexusnet.graph.intelligence:NexusGraphIntelligenceFabric.query",
            "nexusnet.evidence.standards:EvidenceStandardsRuntime.add_node",
            "nexusnet.operations.projection_engine:IncrementalProjectionEngine.project",
        ),
        ("fact-passport", "query-passport", "evolution-passport", "privacy-filter", "content-addressed-evidence-dag", "provenance-crate", "signed-time-receipt", "transparency-receipt", "content-credential", "incremental-projection"),
        r"gitnexus|codegraph|knowledge-structure|evidence-dag|lineage-ledger|authz-graph|evidence-graph|dataflow-projection|graph-intelligence|ai-bom",
    ),
)


_TARGET_GROUPS = {
    1: (
        "55-workflow-engine-substrate-spec", "58-parallel-tool-dag-compiler-spec",
        "65-formal-workflow-model-checking-spec",
    ),
    2: (
        "28-bfcl-tool-calling-spec", "56-prompt-governance-optimization-spec",
        "85-deterministic-starlark-plugin-dsl-spec", "86-cue-constraint-config-kernel-spec",
        "105-capability-rpc-object-fabric-spec",
    ),
    3: (
        "01-agentfloor-routing-ladder-spec", "04-amazing-agent-race-navigation-spec",
        "11-embeddable-agent-core-spec", "16-terminal-bench-sandbox-spec",
        "17-androidworld-mobile-agent-spec", "25-browsergym-web-agent-harness-spec",
        "26-osworld-desktop-agent-spec", "27-swe-bench-code-repair-spec",
        "29-frontier-research-engineering-spec", "30-swe-lancer-commercial-coding-spec",
        "36-clawsbench-productivity-agent-spec", "37-multiagentbench-coordination-spec",
        "38-data-agent-enterprise-query-spec", "39-enterprise-deep-research-spec",
        "40-durable-agent-orchestration-spec", "10-tars-computer-use-operator-spec",
    ),
    4: (
        "12-open-model-runtime-ladder-spec", "41-kv-cache-runtime-efficiency-spec",
        "49-context-compression-governor-spec", "52-llm-gateway-budget-control-spec",
        "57-grammar-constrained-decoder-kernel-spec", "59-adaptive-reasoning-effort-router-spec",
        "68-speculative-decoding-runtime-stack-spec", "70-learned-model-cascade-router-spec",
        "78-verified-semantic-cache-spec", "113-neuromorphic-event-driven-substrate-spec",
        "114-neocortical-microcircuit-reconstruction-spec", "131-liquid-dynamical-cortex-spec",
    ),
    5: (
        "06-clawarena-belief-revision-spec", "19-tau-knowledge-voice-spec",
        "21-agent-memory-stack-spec", "24-astra-personal-context-spec",
        "61-agentic-context-playbook-spec", "64-local-first-crdt-state-spec",
        "120-ancient-memory-palace-spatial-kac-spec", "129-semantic-pointer-binding-substrate-spec",
        "04-agentic-rag-planner-spec",
    ),
    6: (
        "02-clawmark-coworker-eval-spec", "03-agentprocessbench-step-verifier-spec",
        "07-parsebench-document-certification-spec", "08-agentproof-workflow-verification-spec",
        "14-workstream-observability-surface-spec", "18-tau-bench-customer-reliability-spec",
        "31-inspect-ai-evaluation-spine-spec", "42-agent-observability-standards-spec",
        "48-rag-evaluation-harness-spec", "50-model-eval-harness-federation-spec",
        "60-reflective-text-optimization-spec", "66-property-based-agent-testing-spec",
        "80-syscall-runtime-sensor-spec", "81-agent-chaos-failure-injection-spec",
        "100-deterministic-simulation-failure-foundry-spec", "101-runtime-monitor-synthesis-spec",
        "102-assurance-case-evidence-graph-spec", "104-content-credential-evidence-layer-spec",
        "107-digital-twin-simulation-gate-spec", "06-synthetic-truth-guard-spec",
        "07-black-box-interpretability-plane-spec",
    ),
    7: (
        "05-computer-use-safety-reliability-spec", "09-mcp-security-dynamic-red-team-spec",
        "10-protocol-trust-stack-spec", "13-agentic-commerce-authority-spec",
        "20-saber-mutating-action-guard-spec", "32-red-team-toolchain-spec",
        "33-owasp-agentic-skill-risk-spec", "34-toolsandbox-stateful-tool-use-spec",
        "44-five-eyes-agentic-security-spec", "45-policy-as-code-action-pdp-spec",
        "46-agent-identity-delegation-spec", "47-sandbox-isolation-tiering-spec",
        "51-privacy-redaction-preflight-spec", "54-ai-bom-supply-chain-graph-spec",
        "62-object-capability-delegation-spec", "63-hermetic-task-capsule-spec",
        "72-effect-typed-authority-surface-spec", "73-wasm-component-tool-sandbox-spec",
        "74-confidential-ai-execution-envelope-spec", "77-proof-carrying-action-guard-spec",
        "79-private-federated-learning-spec", "82-fine-grained-authz-graph-spec",
        "83-secure-update-trust-root-spec", "87-hardened-js-ocap-compartment-spec",
        "88-biscuit-datalog-capability-token-spec", "89-scitt-supply-chain-receipt-spec",
        "90-zkvm-proof-of-execution-spec", "91-private-compute-crypto-lane-spec",
        "94-landlock-seccomp-micro-sandbox-spec", "95-verifiable-agent-credential-passport-spec",
        "96-static-taint-flow-gate-spec", "97-verified-isolation-kernel-spec",
        "98-capability-hardware-rights-spec",
    ),
    8: (
        "69-verifier-guided-search-controller-spec", "115-global-workspace-consciousness-router-spec",
        "116-active-inference-homeostatic-agent-spec", "117-hippocampal-replay-consolidation-engine-spec",
        "118-bioelectric-morphogenesis-growth-engine-spec", "119-developmental-open-ended-ai-embryo-spec",
        "121-lullian-combinatorial-search-engine-spec", "122-archaic-symbolic-change-calculus-spec",
        "123-cortical-reference-frame-swarm-spec", "124-latent-world-model-imagination-engine-spec",
        "125-continuous-self-model-body-schema-spec", "126-causal-representation-intervention-cortex-spec",
        "127-gflownet-diverse-thought-factory-spec", "128-intrinsic-motivation-empowerment-drive-spec",
        "130-neural-cellular-self-organizing-growth-spec", "132-autopoietic-viability-kernel-spec",
        "133-open-ended-self-improvement-archive-spec", "134-final-missing-piece-developmental-cortex-spec",
        "08-darwin-godel-machine-lineage-spec", "09-alphaevolve-verifier-search-spec",
    ),
    9: ("01-frontier-small-model-training-spec",),
    10: ("23-occubench-professional-faults-spec",),
    11: (
        "15-agent-ui-protocols-spec", "02-jarvis-operator-shell-spec",
        "03-space-agent-self-updating-surface-spec",
    ),
    12: (
        "22-airs-research-lifecycle-spec", "35-enterpriseops-governed-ops-spec",
        "43-artifact-provenance-supply-chain-spec", "75-event-sourced-agent-trace-log-spec",
        "76-feature-flagged-agent-rollout-spec", "84-reversible-patch-transaction-log-spec",
        "92-deterministic-replay-snapshot-spec", "93-reproducible-rebuilder-network-spec",
        "99-flight-software-command-telemetry-bus-spec", "103-scientific-provenance-crate-spec",
        "106-trusted-time-attestation-receipts-spec",
    ),
    13: (
        "53-graphrag-knowledge-structure-spec", "67-content-addressed-evidence-dag-spec",
        "71-data-model-lineage-ledger-spec", "108-incremental-dataflow-projection-engine-spec",
        "05-gitnexus-codegraph-gate-spec",
    ),
}

_PRIMARY_OVERRIDES = {
    target_id: cluster_id
    for cluster_id, target_ids in _TARGET_GROUPS.items()
    for target_id in target_ids
}


class CorpusAssimilationRuntime:
    """Executable, Canon-governed binding layer for the complete numbered corpus."""

    def __init__(
        self,
        *,
        artifacts_dir: Path | str | None = None,
        targets: Iterable[dict[str, Any]] | None = None,
    ) -> None:
        if targets is None:
            from nexusnet.operations.assimilation_catalog import _load_targets

            targets = _load_targets()
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self._targets = {str(item["target_id"]): deepcopy(dict(item)) for item in targets}
        self._clusters = {cluster.cluster_id: cluster for cluster in _CLUSTERS}
        self._handlers: dict[int, Callable[[dict[str, Any]], dict[str, Any]]] = {
            1: self._execute_workflow,
            2: self._execute_skill_protocol,
            3: self._execute_agent_workbench,
            4: self._execute_runtime_ladder,
            5: self._execute_knowledge_memory,
            6: self._execute_eval,
            7: self._execute_authority,
            8: self._execute_imagination,
            9: self._execute_teacher_council,
            10: self._execute_expert_pack,
            11: self._execute_control_surface,
            12: self._execute_operations,
            13: self._execute_graph,
        }
        self._probe_cache: dict[int, dict[str, Any]] = {}

    def binding_for(self, target_id: str) -> dict[str, Any]:
        target = self._targets.get(target_id)
        if target is None:
            raise KeyError(f"unknown assimilation target: {target_id}")
        if target_id in _CANON_EXCLUSIONS:
            return {
                "state": "canon-excluded",
                "exclusion_reason": _CANON_EXCLUSIONS[target_id],
                "production_mutation_allowed": False,
            }
        cluster_ids = self._cluster_ids(target)
        primary_id = _PRIMARY_OVERRIDES.get(target_id, 0)
        if primary_id == 0:
            return {"state": "unbound", "production_mutation_allowed": False}
        cluster = self._clusters[primary_id]
        related = sorted(set(cluster_ids) | {primary_id})
        probe = self._probe_cluster(primary_id)
        return {
            "state": "runtime-implemented" if probe["passed"] else "implementation-probe-failed",
            "cluster_id": primary_id,
            "related_cluster_ids": related,
            "native_output": cluster.native_output,
            "implementation_refs": list(cluster.implementation_refs),
            "verified_capabilities": list(cluster.verified_capabilities),
            "probe": probe,
            "production_mutation_allowed": False,
        }

    def completeness_report(self) -> dict[str, Any]:
        bindings = {target_id: self.binding_for(target_id) for target_id in sorted(self._targets)}
        excluded = [target_id for target_id, item in bindings.items() if item["state"] == "canon-excluded"]
        unbound = [target_id for target_id, item in bindings.items() if item["state"] == "unbound"]
        failures = [
            target_id
            for target_id, item in bindings.items()
            if item["state"] == "implementation-probe-failed"
        ]
        implemented = [target_id for target_id, item in bindings.items() if item["state"] == "runtime-implemented"]
        code_appropriate = len(self._targets) - len(excluded)
        return {
            "surface_id": "complete-corpus-assimilation-runtime",
            "authority": "NexusBrain",
            "target_count": len(self._targets),
            "code_appropriate_target_count": code_appropriate,
            "implemented_target_count": len(implemented),
            "canon_excluded_target_ids": excluded,
            "unbound_target_ids": unbound,
            "probe_failure_target_ids": failures,
            "unimplemented_target_ids": sorted(set(unbound + failures)),
            "runtime_state": (
                "complete-runtime-bindings"
                if len(implemented) == code_appropriate and not unbound and not failures
                else "incomplete-runtime-bindings"
            ),
            "cluster_counts": {
                str(cluster_id): sum(1 for item in bindings.values() if item.get("cluster_id") == cluster_id)
                for cluster_id in self._clusters
            },
            "bindings": bindings,
        }

    def execute(self, target_id: str, *, payload: dict[str, Any]) -> dict[str, Any]:
        binding = self.binding_for(target_id)
        if binding["state"] == "canon-excluded":
            raise PermissionError(binding["exclusion_reason"])
        if binding["state"] != "runtime-implemented":
            raise RuntimeError(f"target is not executable: {target_id}")
        result = self._handlers[binding["cluster_id"]](deepcopy(payload))
        receipt_payload = {"target_id": target_id, "cluster_id": binding["cluster_id"], "result": result}
        return {
            "target_id": target_id,
            "cluster_id": binding["cluster_id"],
            "status": "executed",
            "result": result,
            "production_mutation_allowed": False,
            "receipt_sha256": "sha256:" + hashlib.sha256(
                json.dumps(receipt_payload, sort_keys=True, default=str).encode("utf-8")
            ).hexdigest(),
        }

    def _cluster_ids(self, target: dict[str, Any]) -> list[int]:
        searchable = " ".join(
            str(target.get(key) or "")
            for key in ("target_id", "title", "assimilation_target", "proposed_components")
        )
        return [cluster.cluster_id for cluster in _CLUSTERS if cluster.matcher.search(searchable)]

    def _probe_cluster(self, cluster_id: int) -> dict[str, Any]:
        cached = self._probe_cache.get(cluster_id)
        if cached is not None:
            return deepcopy(cached)
        cluster = self._clusters[cluster_id]
        resolved: list[str] = []
        errors: list[str] = []
        for ref in cluster.implementation_refs:
            try:
                module_name, symbol_path = ref.split(":", 1)
                value: Any = importlib.import_module(module_name)
                for part in symbol_path.split("."):
                    value = getattr(value, part)
                if not callable(value):
                    raise TypeError("resolved object is not callable")
                resolved.append(ref)
            except (ImportError, AttributeError, TypeError, ValueError) as exc:
                errors.append(f"{ref}: {type(exc).__name__}: {exc}")
        handler = self._handlers.get(cluster_id)
        passed = handler is not None and not errors and len(resolved) == len(cluster.implementation_refs)
        probe = {
            "passed": passed,
            "resolved_refs": resolved,
            "errors": errors,
            "handler": handler.__name__ if handler is not None else None,
        }
        self._probe_cache[cluster_id] = probe
        return deepcopy(probe)

    def _execute_workflow(self, payload: dict[str, Any]) -> dict[str, Any]:
        nodes = [str(node) for node in payload.get("nodes") or []]
        if not nodes or len(nodes) != len(set(nodes)):
            raise ValueError("workflow requires unique nodes")
        incoming = {node: 0 for node in nodes}
        outgoing = {node: [] for node in nodes}
        for edge in payload.get("edges") or []:
            if not isinstance(edge, (list, tuple)) or len(edge) != 2:
                raise ValueError("each workflow edge must be [source, target]")
            source, target = map(str, edge)
            if source not in incoming or target not in incoming:
                raise ValueError("workflow edge references an unknown node")
            outgoing[source].append(target)
            incoming[target] += 1
        ready = sorted(node for node, count in incoming.items() if count == 0)
        order: list[str] = []
        while ready:
            node = ready.pop(0)
            order.append(node)
            for target in sorted(outgoing[node]):
                incoming[target] -= 1
                if incoming[target] == 0:
                    ready.append(target)
                    ready.sort()
        if len(order) != len(nodes):
            raise ValueError("workflow graph contains a cycle")
        return {"topological_order": order, "node_count": len(nodes), "cycle_free": True}

    def _execute_skill_protocol(self, payload: dict[str, Any]) -> dict[str, Any]:
        components = [str(item).strip() for item in payload.get("components") or [] if str(item).strip()]
        if not components:
            raise ValueError("at least one skill component is required")
        return {
            "components": components,
            "handoffs": [f"{left}->{right}" for left, right in zip(components, components[1:])],
            "validated": len(components) == len(set(components)),
        }

    def _execute_agent_workbench(self, payload: dict[str, Any]) -> dict[str, Any]:
        tasks = payload.get("tasks") or []
        nodes = [str(item["task_id"]) for item in tasks]
        edges = [
            [str(dependency), str(item["task_id"])]
            for item in tasks
            for dependency in item.get("blocked_by") or []
        ]
        plan = self._execute_workflow({"nodes": nodes, "edges": edges})
        plan["sandbox_required"] = True
        return plan

    def _execute_runtime_ladder(self, payload: dict[str, Any]) -> dict[str, Any]:
        model_gib = max(0.0, float(payload.get("model_size_gib", 0.0)))
        vram_gib = max(0.0, float(payload.get("vram_gib", 0.0)))
        ram_gib = max(0.0, float(payload.get("ram_gib", 0.0)))
        reserve = max(0.5, float(payload.get("vram_reserve_gib", 1.0)))
        usable_vram = max(0.0, vram_gib - reserve)
        if model_gib <= usable_vram:
            placement = "gpu-resident"
        elif model_gib <= usable_vram + max(0.0, ram_gib - 2.0):
            placement = "paged-gpu-cpu-offload"
        else:
            placement = "insufficient-memory"
        return {
            "placement": placement,
            "gpu_resident_gib": min(model_gib, usable_vram),
            "system_ram_offload_gib": max(0.0, model_gib - usable_vram),
            "pinned_host_memory": placement == "paged-gpu-cpu-offload",
            "prefetch_double_buffer": placement == "paged-gpu-cpu-offload",
        }

    def _execute_knowledge_memory(self, payload: dict[str, Any]) -> dict[str, Any]:
        records = list(payload.get("records") or [])
        query = str(payload.get("query") or "").lower()
        hits = [
            deepcopy(record)
            for record in records
            if query and query in json.dumps(record, sort_keys=True).lower()
        ]
        return {"hit_count": len(hits), "hits": hits, "source_grounding_required": True}

    def _execute_eval(self, payload: dict[str, Any]) -> dict[str, Any]:
        scores = {str(key): float(value) for key, value in (payload.get("scores") or {}).items()}
        thresholds = {str(key): float(value) for key, value in (payload.get("thresholds") or {}).items()}
        missing = sorted(set(thresholds) - set(scores))
        failures = sorted(key for key, threshold in thresholds.items() if scores.get(key, float("-inf")) < threshold)
        return {"passed": not missing and not failures, "missing_metrics": missing, "failed_metrics": failures}

    def _execute_authority(self, payload: dict[str, Any]) -> dict[str, Any]:
        blockers = []
        for field in ("evidence_refs", "rollback_plan", "policy_refs"):
            if not payload.get(field):
                blockers.append(f"{field}-required")
        if payload.get("risk") in {"high", "critical"} and not payload.get("operator_approved"):
            blockers.append("operator-approval-required")
        return {"decision": "allow-shadow" if not blockers else "deny", "blockers": blockers}

    def _execute_imagination(self, payload: dict[str, Any]) -> dict[str, Any]:
        hypotheses = [str(item).strip() for item in payload.get("hypotheses") or [] if str(item).strip()]
        evidence_refs = list(payload.get("evidence_refs") or [])
        return {
            "candidates": [{"hypothesis": item, "state": "candidate-only"} for item in hypotheses],
            "evidence_refs": evidence_refs,
            "production_mutation_allowed": False,
        }

    def _execute_teacher_council(self, payload: dict[str, Any]) -> dict[str, Any]:
        teachers = list(payload.get("teachers") or [])
        ranked = sorted(
            teachers,
            key=lambda item: (
                not bool(item.get("rights_verified")),
                not bool(item.get("hardware_fit")),
                -float(item.get("eval_score", 0.0)),
                str(item.get("teacher_id", "")),
            ),
        )
        eligible = [item for item in ranked if item.get("rights_verified") and item.get("hardware_fit")]
        return {"ranked_teachers": ranked, "eligible_teacher_count": len(eligible), "panel_ready": len(eligible) >= 2}

    def _execute_expert_pack(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("domain", "source_refs", "eval_refs", "risk_policy", "teacher_ids", "rollback_plan")
        missing = [field for field in required if not payload.get(field)]
        return {"status": "shadow-ready" if not missing else "blocked", "missing_fields": missing, "retention_review_required": True}

    def _execute_control_surface(self, payload: dict[str, Any]) -> dict[str, Any]:
        private_keys = {"secret", "token", "credential", "raw_trace"}
        sanitized = {key: value for key, value in payload.items() if key.lower() not in private_keys}
        return {"view_state": sanitized, "redacted_keys": sorted(set(payload) - set(sanitized)), "read_only": True}

    def _execute_operations(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("owner", "feature_flag", "evidence_refs", "rollback_plan", "monitoring_ref")
        missing = [field for field in required if not payload.get(field)]
        return {"stage": "shadow" if not missing else "draft", "missing_fields": missing, "rollback_rehearsal_required": True}

    def _execute_graph(self, payload: dict[str, Any]) -> dict[str, Any]:
        query = str(payload.get("query") or "").strip()
        if not query:
            raise ValueError("graph query is required")
        privacy_class = str(payload.get("privacy_class") or "internal")
        if privacy_class not in {"public", "internal", "private", "federated"}:
            raise ValueError("unsupported graph privacy class")
        if self.artifacts_dir is not None:
            from nexusnet.graph.intelligence import NexusGraphIntelligenceFabric

            fabric = NexusGraphIntelligenceFabric(artifacts_dir=self.artifacts_dir)
            passport = fabric.query(
                query_id="corpus-runtime-query",
                terms=[query],
                purpose="assimilation-runtime",
                requester="NexusBrain",
                allowed_privacy_classes=[privacy_class],
            )
            passport["privacy_class"] = privacy_class
        else:
            passport = {
                "passport_kind": "GraphQueryPassport",
                "query_id": "corpus-runtime-query",
                "privacy_class": privacy_class,
                "term_digest": hashlib.sha256(query.encode("utf-8")).hexdigest(),
                "hits": [],
            }
        return {"query_passport": passport, "production_mutation_allowed": False}
