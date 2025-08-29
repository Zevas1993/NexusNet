
from app.core.memory import PlaneAwareBudget
def test_budget():
    planes_cfg = {"planes":[{"name":"a","token_budget_ratio":0.5},{"name":"b","token_budget_ratio":0.5}]}
    p = PlaneAwareBudget(planes_cfg)
    alloc = p.allocate(100)
    assert alloc["a"] + alloc["b"] >= 100
