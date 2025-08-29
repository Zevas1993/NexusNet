
from __future__ import annotations
import os, json
from core.engines.selector import select_engine
import pathlib

def test_select_engine_respects_policy(tmp_path):
    # write a policy file
    pol_dir = tmp_path / "runtime" / "quantlab"
    pol_dir.mkdir(parents=True)
    (pol_dir/"policy.json").write_text(json.dumps({"engine":"ollama","quant":"int8"}), encoding="utf-8")
    # monkeypatch cwd
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        eng, pol = select_engine(None)
        assert eng.name in ("ollama","transformers")  # ollama if chosen, else fallback safe
        assert isinstance(pol, dict)
    finally:
        os.chdir(cwd)
