
from __future__ import annotations
import random

def mask_vector(vec):
    rnd = random.uniform(0.1, 0.9)
    return [v + rnd for v in vec], rnd

def unmask(sum_masked, masks):
    return sum_masked - sum(masks)
