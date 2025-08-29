
from __future__ import annotations
import os, json
from core.quant.policy import get_active_policy
POLICY = "runtime/quantlab/policy.json"
def test_qes_policy_fallback():
    os.makedirs("runtime/quantlab", exist_ok=True)
    with open(POLICY,"w",encoding="utf-8") as f: f.write(json.dumps({"engine":"transformers","quant":"int8"}))
    p = get_active_policy(None)
    assert p.get("engine") == "transformers"
