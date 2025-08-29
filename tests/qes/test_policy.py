
from core.qes.policy import load_config
def test_qes_cfg_loads():
    c=load_config(); assert c.enabled in (True, False)
