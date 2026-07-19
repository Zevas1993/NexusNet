from __future__ import annotations

from nexusnet.operations.assimilation_targets import (
    AssimilationTargetRegistry,
    SkillCheckpointSpec,
    SkillComponentSpec,
    SkillSystemRequest,
)
from nexusnet.operations.skill_system_executor import SkillSystemExecutor


def test_executor_runs_registered_components_with_exact_handoffs():
    observed_inputs: list[dict[str, object]] = []

    def extract_transcript(component: SkillComponentSpec, inputs: dict[str, object]) -> str:
        observed_inputs.append(inputs)
        return f"transcript:{inputs['video_url']}"

    def select_clips(component: SkillComponentSpec, inputs: dict[str, object]) -> list[str]:
        observed_inputs.append(inputs)
        return [f"clip:{inputs['timestamped_transcript']}"]

    executor = SkillSystemExecutor(
        handlers={
            "transcript-extraction": extract_transcript,
            "clip-selection": select_clips,
        }
    )

    result = executor.execute(
        system_id="weekly-video-clips",
        components=[
            SkillComponentSpec(
                skill_id="transcript-extraction",
                purpose="extract timestamps",
                required_input="video_url",
                output="timestamped_transcript",
            ),
            SkillComponentSpec(
                skill_id="clip-selection",
                purpose="select clips",
                required_input="timestamped_transcript",
                output="approved_clips",
            ),
        ],
        initial_context={"video_url": "https://example.test/video"},
    )

    assert result["lifecycle_state"] == "completed"
    assert result["outputs"] == {
        "timestamped_transcript": "transcript:https://example.test/video",
        "approved_clips": ["clip:transcript:https://example.test/video"],
    }
    assert observed_inputs == [
        {"video_url": "https://example.test/video"},
        {"timestamped_transcript": "transcript:https://example.test/video"},
    ]


def test_executor_fails_closed_when_a_required_handoff_is_missing():
    executor = SkillSystemExecutor(handlers={"render": lambda component, inputs: "rendered"})

    result = executor.execute(
        system_id="missing-handoff",
        components=[
            SkillComponentSpec(
                skill_id="render",
                purpose="render a clip",
                required_input="approved_clip_windows",
                output="rendered_clip",
            ),
        ],
        initial_context={},
    )

    assert result["lifecycle_state"] == "blocked_missing_required_input"
    assert result["steps"] == [
        {
            "skill_id": "render",
            "state": "blocked",
            "reason": "missing_required_input",
            "required_input": "approved_clip_windows",
        }
    ]


def test_registry_executes_a_registered_skill_system_instead_of_only_composing_it():
    registry = AssimilationTargetRegistry()
    registry.register_skill_handler(
        "uppercase",
        lambda component, inputs: str(inputs["source_text"]).upper(),
    )

    result = registry.execute_skill_system(
        SkillSystemRequest(
            system_id="uppercase-system",
            goal="Make source text uppercase.",
            components=[
                SkillComponentSpec(
                    skill_id="uppercase",
                    purpose="uppercase a value",
                    required_input="source_text",
                    output="upper_text",
                )
            ],
        ),
        initial_context={"source_text": "nexus"},
    )

    assert result["lifecycle_state"] == "completed"
    assert result["outputs"] == {"upper_text": "NEXUS"}


def test_executor_resumes_after_human_checkpoint_without_replaying_completed_skill():
    invocations: list[str] = []

    def first(component: SkillComponentSpec, inputs: dict[str, object]) -> str:
        invocations.append(component.skill_id)
        return f"review:{inputs['source_text']}"

    def second(component: SkillComponentSpec, inputs: dict[str, object]) -> str:
        invocations.append(component.skill_id)
        return f"published:{inputs['reviewed_text']}"

    executor = SkillSystemExecutor(handlers={"review": first, "publish": second})
    paused = executor.execute(
        system_id="checkpointed-system",
        components=[
            SkillComponentSpec(
                skill_id="review",
                purpose="review source text",
                required_input="source_text",
                output="reviewed_text",
            ),
            SkillComponentSpec(
                skill_id="publish",
                purpose="publish reviewed text",
                required_input="reviewed_text",
                output="published_text",
            ),
        ],
        human_checkpoints=[
            SkillCheckpointSpec(
                checkpoint_id="approve-review",
                after_skill_id="review",
                required=True,
            )
        ],
        initial_context={"source_text": "nexus"},
    )

    assert paused["lifecycle_state"] == "awaiting_human_checkpoint"
    assert paused["pending_checkpoint"] == {
        "checkpoint_id": "approve-review",
        "after_skill_id": "review",
        "approval_policy": "human-review",
    }
    assert invocations == ["review"]

    still_paused = executor.resume(paused["run_id"], approved_checkpoint_ids=[])
    assert still_paused["lifecycle_state"] == "awaiting_human_checkpoint"
    assert invocations == ["review"]

    completed = executor.resume(paused["run_id"], approved_checkpoint_ids=["approve-review"])
    assert completed["lifecycle_state"] == "completed"
    assert completed["outputs"] == {
        "reviewed_text": "review:nexus",
        "published_text": "published:review:nexus",
    }
    assert completed["checkpoint_receipts"] == [
        {
            "checkpoint_id": "approve-review",
            "after_skill_id": "review",
            "approval_policy": "human-review",
            "state": "approved",
        }
    ]
    assert invocations == ["review", "publish"]
