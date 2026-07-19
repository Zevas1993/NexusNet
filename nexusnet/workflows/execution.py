from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Callable, Mapping


NodeHandler = Callable[[dict[str, Any], dict[str, Any]], Any]


class TypedWorkflowExecutor:
    """Executes typed DAG nodes through registered handlers and capability effects."""

    def __init__(self, *, handlers: Mapping[str, NodeHandler]) -> None:
        self.handlers = dict(handlers)

    def execute(self, workflow: dict[str, Any], *, capability_effects: set[str]) -> dict[str, Any]:
        nodes = {str(node["node_id"]): deepcopy(node) for node in workflow.get("nodes") or []}
        if not nodes or len(nodes) != len(workflow.get("nodes") or []):
            raise ValueError("workflow requires unique typed nodes")
        parents = {node_id: [] for node_id in nodes}
        children = {node_id: [] for node_id in nodes}
        incoming = {node_id: 0 for node_id in nodes}
        for edge in workflow.get("edges") or []:
            if not isinstance(edge, (list, tuple)) or len(edge) != 2:
                raise ValueError("workflow edge must be [source, target]")
            source, target = map(str, edge)
            if source not in nodes or target not in nodes:
                raise ValueError("workflow edge references unknown node")
            parents[target].append(source)
            children[source].append(target)
            incoming[target] += 1
        ready = sorted(node_id for node_id, count in incoming.items() if count == 0)
        order: list[str] = []
        while ready:
            node_id = ready.pop(0)
            order.append(node_id)
            for child in sorted(children[node_id]):
                incoming[child] -= 1
                if incoming[child] == 0:
                    ready.append(child)
                    ready.sort()
        if len(order) != len(nodes):
            raise ValueError("workflow contains a cycle")
        outputs: dict[str, Any] = {}
        receipts = []
        for node_id in order:
            node = nodes[node_id]
            kind = str(node.get("kind") or "")
            effect = str(node.get("effect") or "")
            if effect not in capability_effects:
                raise PermissionError(f"node {node_id} requires capability effect {effect}")
            handler = self.handlers.get(kind)
            if handler is None:
                raise KeyError(f"unregistered workflow node kind: {kind}")
            inputs = {parent: outputs[parent] for parent in sorted(parents[node_id])}
            output = handler(deepcopy(node), deepcopy(inputs))
            outputs[node_id] = output
            receipts.append({
                "node_id": node_id,
                "kind": kind,
                "effect": effect,
                "input_refs": sorted(inputs),
                "output_digest": "sha256:" + hashlib.sha256(json.dumps(output, sort_keys=True, default=str).encode()).hexdigest(),
            })
        return {"status": "executed", "execution_order": order, "outputs": outputs, "receipts": receipts}
