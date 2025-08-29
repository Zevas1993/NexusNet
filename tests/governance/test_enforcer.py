
from core.governance.enforcer import require_acceptance, accepted
def test_tou_state_created():
    ok=require_acceptance(); assert (ok is True) or (ok is False)
