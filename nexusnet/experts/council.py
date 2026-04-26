from __future__ import annotations

from pydantic import BaseModel, Field

from nexus.schemas import new_id


class CouncilDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("council"))
    status: str = "shadow_only"
    selected_experts: list[str] = Field(default_factory=list)
    proposals: list[dict] = Field(default_factory=list)
    votes: dict[str, str] = Field(default_factory=dict)
    can_mutate_production: bool = False
    policy_bypass_allowed: bool = False


class ExpertCouncil:
    """Bounded internal deliberation scaffold; the brain remains the authority."""

    def deliberate(self, *, prompt: str, selected_experts: list[str]) -> CouncilDecision:
        proposals = [
            {
                "expert": expert,
                "proposal": f"{expert} proposal is recorded as shadow evidence for: {prompt[:120]}",
                "authority": "advisory_only",
            }
            for expert in selected_experts
        ]
        votes = {expert: "shadow_review" for expert in selected_experts}
        return CouncilDecision(selected_experts=selected_experts, proposals=proposals, votes=votes)
