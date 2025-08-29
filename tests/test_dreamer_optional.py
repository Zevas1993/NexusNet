
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
