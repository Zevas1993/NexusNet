import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import chat, admin, temporal, qes
from .core.config import load_all_configs

app = FastAPI(title="NexusNet API", version="0.5.1a-r22")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configs on startup
@app.on_event("startup")
async def startup_event():
    load_all_configs()

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.5.1a-r22"}

app.include_router(chat.router, prefix="")
app.include_router(admin.router, prefix="/admin")
app.include_router(temporal.router, prefix="/temporal")
app.include_router(qes.router, prefix="/qes")

app.mount("/ui", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "ui")), name="ui")
