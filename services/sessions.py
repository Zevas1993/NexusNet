
from __future__ import annotations
import os, json, time
from pathlib import Path
SESS_DIR = Path("data/sessions")

def _ensure():
    SESS_DIR.mkdir(parents=True, exist_ok=True)

def list_sessions():
    _ensure()
    out = []
    for p in SESS_DIR.glob("*.json"):
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
            out.append({"id": p.stem, "title": j.get("title") or p.stem, "updated": j.get("updated")})
        except Exception:
            out.append({"id": p.stem, "title": p.stem})
    return sorted(out, key=lambda x: x.get("updated") or 0, reverse=True)

def get_session(sid: str):
    _ensure()
    p = SESS_DIR / f"{sid}.json"
    if not p.exists():
        return {"id": sid, "title": sid, "messages": []}
    try:
        return ensure_settings(json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        return {"id": sid, "title": sid, "messages": []}

def save_session(sid: str, data: dict):
    _ensure()
    data["updated"] = int(time.time()); data["last_active"] = data.get("last_active", int(time.time()))
    p = SESS_DIR / f"{sid}.json"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "id": sid}


def delete_session(sid: str):
    _ensure()
    p = SESS_DIR / f"{sid}.json"
    if p.exists():
        p.unlink()
        return {"ok": True}
    return {"ok": False, "error": "not found"}

def rename_session(old: str, new: str):
    _ensure()
    po = SESS_DIR / f"{old}.json"
    pn = SESS_DIR / f"{new}.json"
    if not po.exists():
        return {"ok": False, "error": "not found"}
    if pn.exists():
        return {"ok": False, "error": "target exists"}
    po.rename(pn)
    return {"ok": True, "id": new}

def export_all():
    _ensure()
    out = []
    for p in SESS_DIR.glob("*.json"):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    return {"sessions": out}

def import_bulk(payload: dict):
    _ensure()
    n = 0
    for s in payload.get("sessions", []):
        sid = s.get("id") or f"imported-{n}"
        save_session(sid, s)
        n += 1
    return {"ok": True, "count": n}


def ensure_settings(doc: dict) -> dict:
    s = doc.get("settings") or {}
    s.setdefault("engine", "transformers")
    s.setdefault("capsule", "generalist")
    s.setdefault("rag", {"window": 5}); s.setdefault("as_of", None); s.setdefault("namespaces", ["global"])
    doc["settings"] = s
    return doc
