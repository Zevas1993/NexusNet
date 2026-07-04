"""The AI hive-mind FABRIC - the connective tissue that makes the nodes one organism.

Neural Bus (bandwidth-efficient pose/summary message passing) + HiveBlackboard (stigmergic shared
coordination) + the fractal node graph (core -> orchestrators -> AOs -> experts) wired with typed
contracts, run as one coordinated organism under hive-wide neuroplasticity (everything connected,
sparsely activated, fully observed). Shadow-only.
"""
from __future__ import annotations

from .neural_bus import NeuralBus, NeuralBusMessage
from .blackboard import HiveBlackboard
from .hive_node import HiveNode, NODE_TYPES, EDGE_TYPES
from .sacred_topology import (
    HIVE_MIND_STYLES,
    sacred_layout,
    metatron_chords,
    topology_signature,
)
from .fabric import HiveMindFabric

__all__ = [
    "NeuralBus",
    "NeuralBusMessage",
    "HiveBlackboard",
    "HiveNode",
    "NODE_TYPES",
    "EDGE_TYPES",
    "HIVE_MIND_STYLES",
    "sacred_layout",
    "metatron_chords",
    "topology_signature",
    "HiveMindFabric",
]
