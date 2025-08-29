
from typing import List
from memory.multiplane.store import Memory, PLANES
from training.rzero.seeds import harvest_from_memory
def dream_and_seed(limit: int = 20) -> List[str]:
    mem = Memory()
    return harvest_from_memory(mem, PLANES, limit=limit)
