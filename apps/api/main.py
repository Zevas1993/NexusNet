
from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn, os, json

from core.orchestrator import Orchestrator
from nexusnet.temporal.atomic_extractor import extract_atomic
from nexusnet.temporal.tkg import TKG
from services.metrics_server import app as metrics_app
from services.compliance import app as compliance_app
from services.scheduler import Scheduler

app = FastAPI(title="NexusNet v0.5.1 α — Combined", version="0.5.1a")
orc = Orchestrator("runtime/config/settings.yaml")
SECRETS_PATH = "runtime/config/secrets.json"

class ChatRequest(BaseModel):
    message: str
    capsule: Optional[str] = None
    rag: bool = True
    max_new_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.95

@app.get("/health")
def health():
    return {"ok": True, "version": "0.5.1-alpha"}

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        res = orc.chat(req.message, rag=req.rag, max_new_tokens=req.max_new_tokens, temperature=req.temperature, top_p=req.top_p)
        return {"response": res["text"], "engine": res["engine"], "capsule": req.capsule or "generalist", "rag": req.rag}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/ingest")
def rag_ingest(texts: Optional[List[str]] = Body(default=None), file: UploadFile | None = File(default=None)):
    try:
        if file is not None:
            content = file.file.read().decode("utf-8")
            if file.filename.endswith(".jsonl"):
                docs = [json.loads(line)["text"] if line.strip() else "" for line in content.splitlines() if line.strip()]
            else:
                docs = [content]
        else:
            docs = texts or []
        ids = orc.rag_ingest(docs)
        return {"ok": True, "added": len(ids)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/admin/providers")
def providers_get():
    try:
        with open(SECRETS_PATH,"r",encoding="utf-8") as f: return json.load(f)
    except Exception:
        return {"openrouter": {"enabled": False, "api_key": ""}, "requesty": {"enabled": False, "api_key": ""}}

@app.post("/admin/providers")
def providers_set(data: Dict[str, Any] = Body(...)):
    with open(SECRETS_PATH,"w",encoding="utf-8") as f: json.dump(data,f,indent=2)
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT","8000")))

app.mount('/_metrics', metrics_app)
app.mount('/_compliance', compliance_app)


class TemporalIngestReq(BaseModel):
    texts: list[str]
    source: str | None = "api"
    url: str | None = None

@app.post("/temporal/ingest")
def temporal_ingest(req: TemporalIngestReq):
    try:
        tkg = TKG("runtime/temporal/tkg.sqlite")
        total = 0
        for t in req.texts:
            facts = extract_atomic(t, source=req.source or "api", url=req.url)
            total += tkg.upsert(facts)
        return {"ok": True, "facts_inserted": total}
    except Exception as e:
        raise HTTPException(500, f"Temporal ingest failed: {e}")

@app.get("/temporal/as_of")
def temporal_as_of(query: str, date: str, limit: int = 20):
    try:
        tkg = TKG("runtime/temporal/tkg.sqlite")
        rows = tkg.as_of(query, date)[:max(1, min(limit, 100))]
        return {"ok": True, "count": len(rows), "rows": rows}
    except Exception as e:
        raise HTTPException(500, f"Temporal query failed: {e}")

# Start optional scheduler
scheduler = Scheduler()
scheduler.start()


# ---- WebSocket telemetry ----
class TelemetryHub:
    def __init__(self):
        self.clients: set[WebSocket] = set()
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.add(ws)
    def disconnect(self, ws: WebSocket):
        self.clients.discard(ws)
    async def broadcast(self, data: dict):
        dead = []
        for ws in list(self.clients):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

telemetry = TelemetryHub()

@app.websocket("/ws/telemetry")
async def ws_telemetry(ws: WebSocket):
    await telemetry.connect(ws)
    try:
        while True:
            # keep-alive / ignore inbound
            await ws.receive_text()
    except WebSocketDisconnect:
        telemetry.disconnect(ws)


# Helper: emit chat event from endpoints that call Orchestrator
async def _emit_chat_event(payload: dict):
    try:
        await telemetry.broadcast(payload)
    except Exception:
        pass


@app.get("/admin/router/confusion", response_class=JSONResponse)
def router_confusion():
    import os, json, collections
    path = "runtime/logs/router.log"
    cm = collections.defaultdict(lambda: collections.Counter())
    total = 0
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if not line: continue
                try:
                    obj = json.loads(line)
                    pred = obj.get("predicted")
                    used = obj.get("used")
                    if pred and used:
                        cm[pred][used] += 1
                        total += 1
                except Exception:
                    continue
    # convert to normal dicts
    cm_out = {p: dict(c) for p,c in cm.items()}
    return {"total": total, "matrix": cm_out}


@app.post("/admin/policy/notify")
async def admin_policy_notify(payload: dict):
    # payload example: {"policy":{"engine":"vllm","quant":"int8"}}
    try:
        await telemetry.broadcast({"type":"policy","payload":payload,"ts": __import__('time').time()})
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


from utils.config import get_rag_cfg
from core.rag.pipeline_lite import augment_prompt

@app.post("/chat")
def chat(payload: dict = Body(...)):
    prompt = payload.get("prompt","")
    capsule = payload.get("capsule")
    cfg = get_rag_cfg()
    if cfg.get("enabled"):
        prompt = augment_prompt(prompt, corpus_dir=cfg.get("corpus_dir","data/corpus/sample"), k=int(cfg.get("top_k",3)))
    o = Orchestrator()
    out = o.generate(prompt, capsule=capsule)
    return {"text": out, "capsule": capsule, "policy": getattr(o, "_policy_choice", {}), "rag_lite": cfg.get("enabled", False)}

from scripts.config.validate import run as _cfg_validate

@app.get('/config/validate')
def config_validate():
    return _cfg_validate()


# === r12 additions ===
from typing import Optional, Dict
import json, os, pathlib

_CONNECTOR_STATE = {"default_engine": os.environ.get("DEFAULT_ENGINE","transformers")}

@app.get("/connectors")
def list_connectors():
    from core.engines import registry as _reg  # type: ignore
    status = _reg.status() if hasattr(_reg, "status") else {}
    return {"default": _CONNECTOR_STATE["default_engine"], "status": status}

@app.post("/connectors/select")
def select_connector(payload: Dict[str, str]):
    eng = payload.get("engine","").strip().lower()
    if eng not in ["transformers","ollama","vllm","tgi"]:
        raise HTTPException(status_code=400, detail="unknown engine")
    _CONNECTOR_STATE["default_engine"] = eng
    return {"ok": True, "default": eng}

# --- First-Run Wizard: writes .env and rag.yaml ---
@app.post("/first-run/save")
def first_run_save(payload: Dict):
    # VERY SIMPLE local writer, intended for single-user dev machines
    env_lines = []
    for k,v in payload.get("env",{}).items():
        if isinstance(v, bool):
            v = "1" if v else "0"
        env_lines.append(f"{k}={v}")
    dot = pathlib.Path(".env")
    dot.write_text("\n".join(env_lines), encoding="utf-8")

    # write rag.yaml if provided
    ry = payload.get("rag")
    if ry:
        cfgp = pathlib.Path("runtime/config/rag.yaml")
        cfgp.parent.mkdir(parents=True, exist_ok=True)
        import yaml  # type: ignore
        cfgp.write_text(yaml.safe_dump(ry, sort_keys=False), encoding="utf-8")
    return {"ok": True}


@app.get("/ready")
def ready():
    # filesystem check (write temp)
    import os, tempfile, json
    fs = {"ok": False, "path": None, "error": None}
    try:
        tmpdir = os.path.abspath("tmp")
        os.makedirs(tmpdir, exist_ok=True)
        fd, p = tempfile.mkstemp(prefix="probe_", dir=tmpdir)
        os.write(fd, b"ok")
        os.close(fd)
        os.remove(p)
        fs = {"ok": True, "path": tmpdir}
    except Exception as e:
        fs = {"ok": False, "error": str(e)}

    # engines status
    try:
        from core.engines import registry as _reg  # type: ignore
        engines = _reg.status()
    except Exception as e:
        engines = {"_error": str(e)}

    # config validation (best-effort)
    try:
        from scripts.config.validate import run as _cfg_validate  # type: ignore
        cfg = _cfg_validate()
    except Exception as e:
        cfg = {"_error": str(e)}

    return {"ok": fs.get("ok", False), "fs": fs, "engines": engines, "config": cfg}


@app.get("/healthz")
def healthz():
    return {"ok": True, "version": "v0.5.1a-r12.2"}

@app.get("/version")
def version():
    return {"version": "v0.5.1a-r12.2"}


# --- r12.3: sessions API + demo seeding ---
from services.sessions import list_sessions, get_session, save_session

@app.get("/sessions")
def sessions_list():
    return {"sessions": list_sessions()}

@app.get("/sessions/{sid}")
def sessions_get(sid: str):
    return get_session(sid)

@app.post("/sessions/{sid}")
def sessions_save(sid: str, payload: dict = Body(...)):
    return save_session(sid, payload)

@app.get("/demo/seed")
def demo_seed():
    import os, json, pathlib
    if os.environ.get("DEMO_MODE","1") != "1":
        return {"ok": False, "error": "DEMO_MODE disabled"}
    path = pathlib.Path("data/demos/sessions.json")
    if not path.exists():
        return {"ok": False, "error": "no demo file"}
    demo = json.loads(path.read_text(encoding="utf-8")).get("sessions", [])
    n = 0
    for s in demo:
        save_session(s["id"], s)
        n += 1
    return {"ok": True, "seeded": n}


# --- r12.4: demo toggle, sessions export/import, rename/delete, streaming chat, memory summary ---
import os, json, time
from fastapi.responses import StreamingResponse

@app.get("/demo/toggle")
def demo_toggle(on: str = "1"):
    os.environ["DEMO_MODE"] = "1" if on == "1" else "0"
    return {"ok": True, "DEMO_MODE": os.environ["DEMO_MODE"]}

@app.get("/sessions/export")
def sessions_export():
    from services.sessions import export_all
    return export_all()

@app.post("/sessions/import")
def sessions_import(payload: dict = Body(...)):
    from services.sessions import import_bulk
    return import_bulk(payload)

@app.post("/sessions/{sid}/rename")
def sessions_rename(sid: str, payload: dict = Body(...)):
    from services.sessions import rename_session
    new = payload.get("id") or payload.get("new_id") or ""
    if not new:
        raise HTTPException(status_code=400, detail="missing new id")
    return rename_session(sid, new)

@app.delete("/sessions/{sid}")
def sessions_delete(sid: str):
    from services.sessions import delete_session
    return delete_session(sid)

@app.post("/chat/stream")
def chat_stream(payload: dict = Body(...)):
    # stream chunks from the selected engine (or dry-run text) as SSE
    prompt = payload.get("prompt","")
    capsule = payload.get("capsule","generalist")

    # reuse existing /chat logic if present, else synthesize
    text = ""
    try:
        # Use the engine selector that /chat uses
        from core.engines.selector import select_engine  # type: ignore
        eng, pol = select_engine(capsule)
        text = eng.generate(prompt)
    except Exception:
        text = "[stream] " + prompt

    def gen():
        # naive token chunking by words
        for tok in text.split():
            yield f"data: {tok}\n\n"
            time.sleep(0.02)
        yield "data: [END]\n\n"
    from services.metrics import record_generation
    # rough estimate in stream path handled client-side; set 0 here
    record_generation(tokens=0, ms=0)
    begin_stream()
    resp = StreamingResponse(gen(), media_type="text/event-stream")
    end_stream(0)
    return resp

@app.post("/sessions/{sid}/summary")
def session_summary(sid: str):
    from services.sessions import get_session, save_session
    from services.memory import summarize
    j = get_session(sid)
    j["summary"] = summarize(j.get("messages", []))
    save_session(sid, j)
    return {"ok": True, "id": sid, "summary": j["summary"]}


@app.post("/sessions/{sid}/settings")
def sessions_update_settings(sid: str, payload: dict = Body(...)):
    from services.sessions import get_session, save_session, ensure_settings
    j = get_session(sid)
    j = ensure_settings(j)
    s = j.get("settings", {})
    for k,v in payload.items():
        if k == "rag" and isinstance(v, dict):
            s.setdefault("rag", {}).update(v)
        else:
            s[k] = v
    j["settings"] = s
    save_session(sid, j)
    return {"ok": True, "id": sid, "settings": s}


# r12.5 helpers for /chat: store context and apply per-session defaults
def _apply_session_defaults(payload: dict):
    sid = payload.get("sid") or payload.get("session_id")
    if not sid:
        return payload, None, None
    from services.sessions import get_session, ensure_settings
    j = ensure_settings(get_session(sid))
    s = j.get("settings", {})
    # default capsule/engine if not provided
    if not payload.get("capsule"): payload["capsule"] = s.get("capsule","generalist")
    payload["_engine_override"] = s.get("engine")
    payload["_rag_window"] = int((s.get("rag") or {}).get("window", 5)); payload['_as_of'] = s.get('as_of'); payload['_namespaces'] = s.get('namespaces')
    return payload, sid, j

def _chat_with_context(prompt: str, capsule: str, rag_window: int, as_of_ts: int | None, namespaces=None):
    # Try new auto pipeline (pgvector or lite)
    try:
        from core.rag.retriever import get_context_hybrid as ctx_auto  # type: ignore
        ctx = ctx_auto(prompt, as_of_ts=as_of_ts, namespaces=namespaces)[:max(1, rag_window)]
    except Exception:
        try:
            from core.rag.retriever import get_context as ctx_lite  # type: ignore
            ctx = ctx_lite(prompt, as_of_ts=as_of_ts, namespaces=namespaces)[:max(1, rag_window)]
        except Exception:
            ctx = []
    # Build augmented prompt (simple concat for $0 path)
    context_text = "\n\n".join([c.get("text","") for c in ctx])
    aug = prompt if not context_text else f"{context_text}\n\nQuestion: {prompt}"
    # Select engine (respect override if selector supports it)
    try:
        from core.engines.selector import select_engine  # type: ignore
        eng, pol = select_engine(capsule)
    except Exception as e:
        class _E: 
            def generate(self, p, **kw): return "[dry] " + p
        eng = _E(); pol=None
    txt = eng.generate(aug)
    return txt, ctx

@app.post("/chat2")
def chat2(payload: dict = Body(...)):
    # New chat endpoint that honors per-session defaults and stores context into session memory
    prompt = payload.get("prompt","")
    capsule = payload.get("capsule")
    payload, sid, doc = _apply_session_defaults(payload)
    capsule = payload.get("capsule","generalist")
    rag_window = payload.get("_rag_window") or 5
    text, ctx = _chat_with_context(prompt, capsule, rag_window, payload.get('_as_of'), payload.get('_namespaces'))

    # store message & retrieved ctx in the session if sid provided
    if sid:
        from services.sessions import save_session
        msgs = (doc.get("messages") or []) + [{"role":"user","content":prompt},{"role":"assistant","content":text,"context":ctx}]
        doc["messages"] = msgs
        doc["last_active"] = int(time.time())
        save_session(sid, doc)

    from services.metrics import record_generation
    record_generation(tokens=count_tokens(text), ms=0)
    return {"text": text, "capsule": capsule, "ctx": ctx, "sid": sid}


@app.get("/compliance/purge")
def compliance_purge(before: str = ""):
    from services import sessions_sqlite as ssql

    import os, time, glob
    from datetime import datetime
    try:
        cutoff = int(datetime.fromisoformat(before).timestamp()) if before else int(time.time())
    except Exception:
        raise HTTPException(status_code=400, detail="bad date")
    removed=0
    removed += ssql.purge(cutoff)
    return {"ok": True, "removed": removed}


@app.get("/metrics")
def prom_metrics():
    sample_system()
    from services.metrics import render_prom, sample_system, count_tokens, begin_stream, tick_stream, end_stream
    return Response(render_prom(), media_type="text/plain")


@app.get("/temporal/timeline")
def temporal_timeline(entity: str, buckets: int = 10):
    from temporal.tkg import timeline
    try:
        b = int(buckets)
    except Exception:
        b = 10
    return {"entity": entity, "timeline": timeline(entity, b)}


@app.get("/admin/overrides")
def admin_overrides_get():
    import json
    try:
        j = json.loads(open("runtime/config/runtime_overrides.json","r",encoding="utf-8").read())
    except Exception:
        j = {}
    return j

@app.post("/admin/overrides")
def admin_overrides_set(payload: dict = Body(...)):
    import json, os
    os.makedirs("runtime/config", exist_ok=True)
    with open("runtime/config/runtime_overrides.json","w",encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return {"ok": True}


@app.get("/temporal/namespaces")
def list_namespaces():
    import yaml, os
    try:
        cfg = yaml.safe_load(open("runtime/config/temporal.yaml","r",encoding="utf-8"))
    except Exception:
        cfg = {}
    ns = (cfg.get("namespaces") or {}).get("list") or ["global","medical","code","legal","finance","vision","audio"]
    return {"namespaces": ns}
