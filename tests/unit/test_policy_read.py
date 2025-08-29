
from core.quant.policy import get_active_policy
def test_policy_fallback():
    p = get_active_policy(None)
    assert isinstance(p, dict)
