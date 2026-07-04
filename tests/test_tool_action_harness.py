from nexusnet.tools.action_harness import ToolActionHarness


def test_tool_action_harness_allows_readonly_observation(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id="tool:browser:observe",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:observe"],
    )

    assert result["status"] == "planned-shadow"
    assert result["execution_allowed"] is False
    assert result["operator_confirmation_required"] is False


def test_tool_action_harness_requires_confirmation_for_mutation(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id="tool:desktop:click",
        tool_ref="desktop",
        action_type="click",
        requested_effect="desktop",
        contains_private_data=True,
        sandbox_state="none",
        operator_approved=False,
        evidence_refs=["trace:click"],
    )

    assert result["status"] == "blocked"
    assert result["operator_confirmation_required"] is True
    assert "mutating_tool_action_requires_sandbox" in result["findings"]
