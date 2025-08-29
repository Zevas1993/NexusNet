
from core.safe.controller import advise
def test_advise_keys():
    out=advise(); assert set(['risk','vram_pct','cpu_temp','gpu_temp','action']).issubset(set(out.keys()))
