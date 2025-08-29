
from app.core.inference import InferenceSelector
def test_select():
    s = InferenceSelector()
    b = s.select_backend()
    assert b is not None
