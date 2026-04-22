from __future__ import annotations

from pathlib import Path

import yaml

from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_teacher_registry_loads_historical_and_live_layers(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    metadata = services.brain_teachers.metadata()
    assert metadata["schema_version"] == 2
    assert metadata["default_registry_layer"] == "v2026_live"

    historical = metadata["registry_layers"]["historical"]
    assert historical["central_brain_mentor_ensemble"]["teacher_names"] == [
        "Mixtral-8x7B",
        "Yi-1.5-9B",
        "Qwen-0.5B-MoE",
        "LLaMA-3-8B",
    ]
    assert historical["historical_principles"]["best_ensemble_per_role"] is True
    assert historical["historical_principles"]["one_teacher_per_role"] is False

    live = metadata["registry_layers"]["v2026_live"]
    assert "core_brain_live_mentor_pool" in live["global_live_pools"]
    assert "remote_frontier_pool" in live["global_live_pools"]

    historical_coder = services.brain_teachers.assignment_for("coder", "historical")
    live_coder = services.brain_teachers.assignment_for("coder", "v2026_live")
    assert historical_coder is not None
    assert live_coder is not None
    assert historical_coder.routing_mode == "best-ensemble-per-role"
    assert live_coder.primary_teacher_id == "qwen3-coder-next"
    assert live_coder.secondary_teacher_id == "devstral-2"
    assert historical_coder.teacher_ids != live_coder.teacher_ids


def test_live_roster_preserves_19_core_and_auxiliary_curriculum_architect(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    live_core = [
        assignment
        for assignment in services.brain_teachers.list_assignments()
        if assignment.registry_layer == "v2026_live"
        and assignment.subject != "core-brain"
        and not assignment.auxiliary
        and assignment.primary_teacher_id
        and assignment.secondary_teacher_id
    ]
    assert len(live_core) == 19
    assert sorted(assignment.roster_position for assignment in live_core) == list(range(1, 20))

    curriculum = services.brain_teachers.assignment_for("curriculum-architect", "v2026_live")
    assert curriculum is not None
    assert curriculum.auxiliary is True
    assert curriculum.status_label == "STRONG ACCEPTED DIRECTION"
    assert curriculum.roster_position is None


def test_historical_registry_preserves_exact_canonical_ensembles(tmp_path):
    make_project(tmp_path)
    historical_path = Path(__file__).resolve().parents[1] / "nexusnet" / "teachers" / "teacher_registry_historical.yaml"
    payload = yaml.safe_load(historical_path.read_text(encoding="utf-8"))

    assert payload["central_brain_mentor_ensemble"]["teacher_names"] == [
        "Mixtral-8x7B",
        "Yi-1.5-9B",
        "Qwen-0.5B-MoE",
        "LLaMA-3-8B",
    ]
    assert payload["historical_principles"] == {
        "best_ensemble_per_role": True,
        "one_teacher_per_role": False,
        "teachers_discarded_after_surpass": True,
        "post_bootstrap_transition": [
            "Recursive Neural Dreaming",
            "Federated Learning",
            "Consequence Feedback Routing",
        ],
    }
    expected_ensembles = {
        "Coder Expert": ["CodeStral", "Code LLaMA 7B/13B", "StarCoder", "DeepSeek-Coder", "PolyCoder"],
        "Strategist Expert": ["Mixtral-8x7B", "GPT4All-Strategy-tuned", "Yi-1.5-9B", "OpenHermes-2.5"],
        "Analyst Expert": ["LLaMA-3-8B", "MPT-Instruct", "Falcon-Instruct", "Orca-2"],
        "Researcher Expert": ["SciBERT", "BioMedLM", "Galactica", "LLaMA-3-8B research-tuned"],
        "Critique Expert": ["Claude-Eval fine-tunes", "Alpaca-Eval-tuned LLaMA", "OpenHermes-Critique"],
        "Conversationalist Expert": ["Yi-1.5-9B", "Vicuna-13B", "OpenChat-3.5", "Mistral-Instruct"],
        "Toolsmith Expert": ["ToolBench-trained LLaMA", "Gorilla API-Agent model", "Mistral-Toolformer"],
        "Security Expert": ["CyberSecEval LLMs", "GPT-J security fine-tunes", "Code LLaMA-Secure"],
        "Memory Weaver Expert": ["MemGPT", "LongLoRA LLaMA-3-8B", "RecurrentGemma memory-tuned"],
        "Meta Reasoner Expert": ["Mixtral-8x7B", "DeepSeek-R1", "LLaMA-3-70B distilled outputs"],
        "Router Expert": ["MoE-Router-LLaMA", "Switch-Transformers", "Qwen-MoE-0.5B"],
        "Linguist Expert": ["MPT-Storywriter", "Falcon-Instruct", "Yi-1.5-9B", "BLOOMZ"],
        "Vision Expert": ["OpenCLIP", "BLIP-2", "SAM", "EVA-CLIP"],
        "Audio Expert": ["Whisper-Large-V3", "Wav2Vec 2.0", "AudioLM", "Bark-TTS"],
        "Simulation Expert": ["MuZero", "Dreamer-V3", "World Models", "GenSimRL"],
        "Builder Expert": ["LLaMA-3-8B", "Mistral-Instruct", "WizardCoder-Builder"],
        "Instructor Expert": ["OpenHermes-2.5-Instruct", "Vicuna-13B-Instruct", "Yi-1.5-Instruct"],
        "Intent Mapper Expert": ["Intent-BERT", "Qwen-0.5B-MoE", "DistilBERT-Intent"],
        "Critic Historian Expert": ["Claude-Eval-Historical", "LLaMA-Historian-tuned", "Alpaca-Eval"],
    }
    assert {
        role: details["teacher_names"] for role, details in payload["expert_role_ensembles"].items()
    } == expected_ensembles


def test_live_registry_preserves_exact_primary_secondary_pairs(tmp_path):
    make_project(tmp_path)
    live_path = Path(__file__).resolve().parents[1] / "nexusnet" / "teachers" / "teacher_registry_v2026_live.yaml"
    payload = yaml.safe_load(live_path.read_text(encoding="utf-8"))
    live_pairs = payload["live_expert_pairs"]

    assert len(live_pairs) == 19
    expected_pairs = {
        "Coder Expert": ("Qwen3-Coder-Next", "Devstral 2", None),
        "Strategist Expert": ("Qwen3-30B-A3B", "Magistral Small 1.2", None),
        "Analyst Expert": ("DeepSeek-R1-Distill-Qwen-32B", "Qwen3-30B-A3B", None),
        "Researcher Expert": ("Qwen3-30B-A3B", "Kimi K2.5", None),
        "Critique Expert": ("DeepSeek-R1-Distill-Qwen-32B", "Qwen3-30B-A3B", None),
        "Conversationalist Expert": ("Mistral Small 4", "Qwen3-30B-A3B", None),
        "Toolsmith Expert": ("Devstral 2", "Qwen3-Coder-Next", "LFM2"),
        "Security Expert": ("Code LLaMA-Secure", "Devstral 2", "LFM2"),
        "Memory Weaver Expert": ("RecurrentGemma memory-tuned", "DeepSeek-V2-Lite", "LFM2"),
        "Meta Reasoner Expert": ("DeepSeek-R1-Distill-Qwen-32B", "Qwen3-30B-A3B", None),
        "Router Expert": ("DeepSeek-V2-Lite", "Qwen3-30B-A3B", "LFM2"),
        "Linguist Expert": ("Qwen3-30B-A3B", "BLOOMZ", None),
        "Vision Expert": ("Qwen3-VL", "Kimi K2.5", None),
        "Audio Expert": ("Voxtral Small", "Whisper-Large-V3", None),
        "Simulation Expert": ("Dreamer-V3", "MuZero", None),
        "Builder Expert": ("Devstral 2", "Mistral Small 4", None),
        "Instructor Expert": ("Qwen3-30B-A3B", "Mistral Small 4", None),
        "Intent Mapper Expert": ("Intent-BERT", "Qwen3-30B-A3B", None),
        "Critic Historian Expert": ("LLaMA-Historian-tuned", "DeepSeek-R1-Distill-Qwen-32B", None),
    }
    assert {
        role: (
            details["primary_teacher"],
            details["secondary_teacher"],
            details["optional_efficiency_coach"],
        )
        for role, details in live_pairs.items()
    } == expected_pairs
    assert live_pairs["Security Expert"]["evaluation_family"] == ["CyberSecEval"]
    assert payload["auxiliary_paths"]["Curriculum Architect"]["canon_status"] == "STRONG ACCEPTED DIRECTION"
