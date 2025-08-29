
#!/usr/bin/env python3
from __future__ import annotations
from core.fl.coordinator import Coordinator
from core.fl.dp import add_gaussian_noise
import random

def main():
    C = Coordinator(min_clients=2, round_timeout=5)
    a = [random.uniform(-1,1) for _ in range(16)]
    b = [random.uniform(-1,1) for _ in range(16)]
    C.submit("A", add_gaussian_noise(a, 0.02))
    C.submit("B", add_gaussian_noise(b, 0.02))
    res = C.aggregate()
    print(res)
if __name__ == "__main__":
    main()
