
import importlib
import pytest

def test_dreamer_optional_present_or_skip():
    spec = importlib.util.find_spec("recursive_dreamer.loop")
    if spec is None:
        pytest.skip("Dreamer module not present; optional feature.")
    mod = importlib.import_module("recursive_dreamer.loop")
    assert hasattr(mod, "dream_once")
    out = mod.dream_once("Hello", "Draft answer")
    assert isinstance(out, str)


def test_dream_once_preserves_draft_and_adds_deterministic_relevance_critique():
    from recursive_dreamer.loop import dream_once

    prompt = "Explain memory bandwidth bottlenecks and evidence for GPU inference."
    draft = "Limited VRAM can slow model execution."

    first = dream_once(prompt, draft)
    second = dream_once(prompt, draft)

    assert first == second
    assert first.startswith(draft)
    assert "Dream refinement:" in first
    assert "memory" in first.lower()
    assert "evidence" in first.lower()
    assert len(first) <= 32768


def test_dream_once_handles_empty_draft_and_rejects_non_string_inputs():
    from recursive_dreamer.loop import dream_once

    result = dream_once("Give a safe answer with explicit evidence.", "")

    assert isinstance(result, str)
    assert result.strip()
    assert "Dream refinement:" in result
    with pytest.raises(TypeError, match="prompt and draft must be strings"):
        dream_once("valid", None)
