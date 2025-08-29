
from __future__ import annotations
import os
import uvicorn
def main():
    # Import FastAPI app dynamically (works whether module is package or plain file)
    try:
        from apps.api.main import app
    except Exception:
        # fallback: older layout
        from apps.api import main as _m
        app = getattr(_m, "app", None)
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="127.0.0.1", port=port)
