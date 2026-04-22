from __future__ import annotations

from ..adapter_registry import AdapterRegistry
from ..cortex import CortexPeerService
from ..mixtral_devstral import MixtralDevstralHarness
from ..neural_bus import NeuralBusService
from ..router_alignment import ExpertRouterAlignmentService


class MoEFusionScaffoldService:
    def __init__(
        self,
        *,
        registry: AdapterRegistry | None = None,
        harness: MixtralDevstralHarness | None = None,
        alignment: ExpertRouterAlignmentService | None = None,
        neural_bus: NeuralBusService | None = None,
        cortex_peer: CortexPeerService | None = None,
    ):
        self.registry = registry or AdapterRegistry()
        self.harness = harness or MixtralDevstralHarness()
        self.alignment = alignment or ExpertRouterAlignmentService(registry=self.registry)
        self.neural_bus = neural_bus or NeuralBusService()
        self.cortex_peer = cortex_peer or CortexPeerService()

    def execution_plan(
        self,
        *,
        selected_expert: str | None = None,
        memory_node_context: dict | None = None,
        hardware_profile: dict | None = None,
    ) -> dict:
        harness = self.harness.build(selected_expert=selected_expert)
        alignment = self.alignment.snapshot(router_id=harness["router_id"], expert_ids=harness["expert_ids"])
        return {
            "status_label": "IMPLEMENTATION BRANCH",
            "branch_lineage": harness["branch_lineage"],
            "backbone": harness["backbone"],
            "router": harness["router_id"],
            "expert_ids": harness["expert_ids"],
            "devstral_integrated": harness["devstral_integrated"],
            "mini_nexusnet_per_expert": harness["mini_nexusnet_per_expert"],
            "cortex_peer": self.cortex_peer.snapshot(memory_node_context=memory_node_context),
            "neural_bus": self.neural_bus.snapshot(memory_node_context=memory_node_context),
            "alignment": alignment,
            "native_execution_ceiling": alignment.get("max_safe_native_mode"),
            "alignment_hold_required": alignment.get("alignment_hold_required", False),
            "hardware_note": (
                "Safe-mode hardware detected; fusion remains scaffold-only."
                if (hardware_profile or {}).get("safe_mode")
                else "Hardware posture allows scaffold execution and bounded harness validation."
            ),
            "registry_components": self.registry.list_specs(),
        }
