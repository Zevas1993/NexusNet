from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from threading import RLock
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    from nexusnet.operations.assimilation_targets import SkillCheckpointSpec, SkillComponentSpec


SkillHandler = Callable[[Any, dict[str, Any]], Any]


class SkillSystemExecutor:
    """Runs registered, local skills with explicit context handoffs."""

    def __init__(self, *, handlers: Mapping[str, SkillHandler] | None = None):
        self._handlers = dict(handlers or {})
        self._runs: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    def register(self, skill_id: str, handler: SkillHandler) -> None:
        self._handlers[skill_id] = handler

    def execute(
        self,
        *,
        system_id: str,
        components: list[SkillComponentSpec],
        initial_context: Mapping[str, Any],
        human_checkpoints: list[SkillCheckpointSpec] | None = None,
    ) -> dict[str, Any]:
        checkpoints = list(human_checkpoints or [])
        self._validate_checkpoints(components, checkpoints)
        run_id = f"skill-run-{uuid4().hex}"
        run = {
            "run_id": run_id,
            "system_id": system_id,
            "components": deepcopy(components),
            "checkpoints_by_skill": {
                checkpoint.after_skill_id: deepcopy(checkpoint)
                for checkpoint in checkpoints
            },
            "context": deepcopy(dict(initial_context)),
            "outputs": {},
            "steps": [],
            "checkpoint_receipts": [],
            "pending_checkpoint": None,
            "next_component_index": 0,
            "lifecycle_state": "running",
        }
        with self._lock:
            self._runs[run_id] = run
            return self._advance(run)

    def resume(self, run_id: str, *, approved_checkpoint_ids: list[str]) -> dict[str, Any]:
        with self._lock:
            run = self._runs.get(run_id)
            if run is None:
                raise KeyError(f"unknown skill-system run: {run_id}")

            pending = run.get("pending_checkpoint")
            if pending is None:
                return self._run_result(run)
            if pending["checkpoint_id"] not in set(approved_checkpoint_ids):
                return self._run_result(run)

            run["checkpoint_receipts"].append(
                {
                    **deepcopy(pending),
                    "state": "approved",
                }
            )
            run["pending_checkpoint"] = None
            run["lifecycle_state"] = "running"
            return self._advance(run)

    def _advance(self, run: dict[str, Any]) -> dict[str, Any]:
        components = run["components"]
        context = run["context"]
        outputs = run["outputs"]
        steps = run["steps"]

        for index in range(run["next_component_index"], len(components)):
            component = components[index]
            component_inputs = self._component_inputs(component, context)
            if component_inputs is None:
                steps.append(
                    {
                        "skill_id": component.skill_id,
                        "state": "blocked",
                        "reason": "missing_required_input",
                        "required_input": deepcopy(component.required_input),
                    }
                )
                run["lifecycle_state"] = "blocked_missing_required_input"
                return self._run_result(run)

            handler = self._handlers.get(component.skill_id)
            if handler is None:
                steps.append(
                    {
                        "skill_id": component.skill_id,
                        "state": "blocked",
                        "reason": "unregistered_skill_handler",
                    }
                )
                run["lifecycle_state"] = "blocked_unregistered_skill_handler"
                return self._run_result(run)

            produced = handler(component, deepcopy(component_inputs))
            if not isinstance(component.output, str):
                steps.append(
                    {
                        "skill_id": component.skill_id,
                        "state": "blocked",
                        "reason": "non_addressable_output_contract",
                    }
                )
                run["lifecycle_state"] = "blocked_non_addressable_output_contract"
                return self._run_result(run)

            context[component.output] = produced
            outputs[component.output] = produced
            steps.append(
                {
                    "skill_id": component.skill_id,
                    "state": "completed",
                    "input_keys": sorted(component_inputs),
                    "output_key": component.output,
                }
            )
            run["next_component_index"] = index + 1

            checkpoint = run["checkpoints_by_skill"].get(component.skill_id)
            if checkpoint is not None:
                checkpoint_payload = {
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "after_skill_id": checkpoint.after_skill_id,
                    "approval_policy": checkpoint.approval_policy,
                }
                if checkpoint.required:
                    run["pending_checkpoint"] = checkpoint_payload
                    run["lifecycle_state"] = "awaiting_human_checkpoint"
                    return self._run_result(run)
                run["checkpoint_receipts"].append(
                    {**checkpoint_payload, "state": "not_required"}
                )

        run["lifecycle_state"] = "completed"
        return self._run_result(run)

    @staticmethod
    def _validate_checkpoints(
        components: list[SkillComponentSpec],
        checkpoints: list[SkillCheckpointSpec],
    ) -> None:
        component_ids = {component.skill_id for component in components}
        checkpoint_ids: set[str] = set()
        checkpoint_skills: set[str] = set()
        for checkpoint in checkpoints:
            if checkpoint.after_skill_id not in component_ids:
                raise ValueError(
                    f"checkpoint {checkpoint.checkpoint_id!r} references unknown skill "
                    f"{checkpoint.after_skill_id!r}"
                )
            if checkpoint.checkpoint_id in checkpoint_ids:
                raise ValueError(f"duplicate checkpoint id: {checkpoint.checkpoint_id}")
            if checkpoint.after_skill_id in checkpoint_skills:
                raise ValueError(f"multiple checkpoints after skill: {checkpoint.after_skill_id}")
            checkpoint_ids.add(checkpoint.checkpoint_id)
            checkpoint_skills.add(checkpoint.after_skill_id)

    @staticmethod
    def _component_inputs(component: SkillComponentSpec, context: dict[str, Any]) -> dict[str, Any] | None:
        required_input = component.required_input
        if isinstance(required_input, str):
            if required_input not in context:
                return None
            return {required_input: context[required_input]}

        if not all(key in context for key in required_input):
            return None
        return {key: context[key] for key in required_input}

    @staticmethod
    def _run_result(run: dict[str, Any]) -> dict[str, Any]:
        lifecycle_state = run["lifecycle_state"]
        return {
            "run_id": run["run_id"],
            "system_id": run["system_id"],
            "lifecycle_state": lifecycle_state,
            "runtime_state": "live-bound" if lifecycle_state == "completed" else "blocked",
            "steps": deepcopy(run["steps"]),
            "outputs": deepcopy(run["outputs"]),
            "pending_checkpoint": deepcopy(run.get("pending_checkpoint")),
            "checkpoint_receipts": deepcopy(run["checkpoint_receipts"]),
        }
