
#!/usr/bin/env python3
from __future__ import annotations
import json, os
try:
    from apps.api.main import app
except Exception:
    from apps.api import main as _m
    app = getattr(_m, "app", None)
open("runtime/openapi.json","w",encoding="utf-8").write(json.dumps(app.openapi(), indent=2))
print("wrote runtime/openapi.json")
