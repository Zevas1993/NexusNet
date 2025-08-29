
#!/usr/bin/env bash
python - <<'PY'
from core.fl.coordinator import Coordinator
from core.fl.secagg import mask_vector, unmask
import random

C = Coordinator(min_clients=2, round_timeout=5)
# client A
va,ma = mask_vector([1.0,2.0,3.0])
C.submit("A", va)
# client B
vb,mb = mask_vector([2.0,2.0,2.0])
C.submit("B", vb)
res = C.aggregate()
print("Aggregate:", res)
PY
