
from __future__ import annotations
import random, math

def add_gaussian_noise(vec, sigma: float = 0.01):
    return [v + random.gauss(0.0, sigma) for v in vec]
