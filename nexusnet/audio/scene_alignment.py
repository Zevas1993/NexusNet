"""PB-2026-06-03-098 - Dialogue Voice Scene Alignment Lane (RESEARCH_ONLY; alignment only, NO synthesis).

Canon doctrine: SwanVoice is useful for the audio roadmap but NOT as an unrestricted voice-cloning
target. The accepted research target is dialogue-SCENE ALIGNMENT: speaker turns, pause-aware
alignment, long-form continuity, optional narrated replay. Generated speech is presentation output
only and CANNOT satisfy evidence gates. Forced alignment is the immediately-useful part (it improves
video/audio assimilation + replay). Voice consent + audio rights + provenance gate everything.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

STATUS = "research_only"


class Speaker(BaseModel):
    model_config = ConfigDict(extra="forbid")

    speaker_id: str
    consent_ref: str = ""                # required for any use; empty => not consented
    style_label: str = ""


class Turn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    turn_id: str
    speaker_id: str
    text: str
    pause_before_s: float = 0.0


class AudioScene(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_id: str
    speakers: list[Speaker] = Field(default_factory=list)
    turns: list[Turn] = Field(default_factory=list)
    provenance: str = ""
    watermarked: bool = False
    rights_cleared: bool = False


def consent_gate(scene: AudioScene) -> dict[str, Any]:
    """Every speaker must carry a consent ref, and the scene must be rights-cleared + provenance-marked."""
    missing = [s.speaker_id for s in scene.speakers if not s.consent_ref]
    reasons: list[str] = []
    if missing:
        reasons.append(f"missing_consent:{missing}")
    if not scene.rights_cleared:
        reasons.append("rights_not_cleared")
    if not scene.provenance:
        reasons.append("missing_provenance")
    return {"approved": not reasons, "reasons": reasons}


def forced_align(scene: AudioScene, *, total_duration_s: float) -> dict[str, Any]:
    """Deterministically align turns to a timeline: pauses honored, remaining time split by text length,
    monotonic non-overlapping turn boundaries preserved (this is the alignment, not synthesis)."""
    turns = scene.turns
    if not turns or total_duration_s <= 0:
        return {"aligned": [], "monotonic": True, "coverage": 0.0}
    total_pause = sum(t.pause_before_s for t in turns)
    speech_budget = max(0.0, total_duration_s - total_pause)
    total_chars = sum(max(1, len(t.text)) for t in turns)
    cursor = 0.0
    aligned: list[dict[str, Any]] = []
    for t in turns:
        cursor += t.pause_before_s
        dur = speech_budget * (max(1, len(t.text)) / total_chars)
        start, end = cursor, cursor + dur
        aligned.append({"turn_id": t.turn_id, "speaker_id": t.speaker_id,
                        "start_s": round(start, 4), "end_s": round(end, 4)})
        cursor = end
    monotonic = all(aligned[i]["end_s"] <= aligned[i + 1]["start_s"] + 1e-6
                    for i in range(len(aligned) - 1))
    coverage = (aligned[-1]["end_s"] / total_duration_s) if aligned else 0.0
    return {"aligned": aligned, "monotonic": monotonic, "coverage": round(coverage, 4)}


def synthesize(*_args, **_kwargs) -> dict[str, Any]:
    """Voice synthesis is NOT implemented in this lane. Any synthetic speech is presentation-only and
    is explicitly EXCLUDED from evidence gates (canon PB-098)."""
    return {
        "implemented": False,
        "status": STATUS,
        "synthetic_output_excluded_from_evidence": True,
        "reason": "voice synthesis blocked pending consent/rights/content-accuracy gates",
    }
