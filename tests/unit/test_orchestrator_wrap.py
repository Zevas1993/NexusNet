
from core.orchestrator import Orchestrator
def test_wrap():
    o = Orchestrator()
    s = o.generate("ping", capsule="code")
    assert isinstance(s, str)
