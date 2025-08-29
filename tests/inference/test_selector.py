
from core.inference.selector import pick
def test_selector_returns_tuple():
    b,c = pick()
    assert isinstance(b,str) and isinstance(c,dict)
