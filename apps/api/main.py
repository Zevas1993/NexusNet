"""FastAPI main application for NexusNet"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
from pathlib import Path

# Import core modules
from core.config import load_config, save_config, BASE_DIR
from core.hw.scan import scan_hardware
from core.hw.autotune import apply_autotune
from core.ops.audit import audit_logger

# Initialize FastAPI app
app = FastAPI(
    title="NexusNet API",
    description="Unified AI Framework with HiveMind and Hybrid RAG",
    version="1.0.0"
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    expert: str
    confidence: float
    processing_time: float

class ConfigRequest(BaseModel):
    config: Dict[str, Any]

class KeysRequest(BaseModel):
    openrouter_api_key: Optional[str] = None
    requesty_api_key: Optional[str] = None

# Mount static files
ui_dir = BASE_DIR / "ui"
if ui_dir.exists():
    app.mount("/static", StaticFiles(directory=str(ui_dir)), name="static")

# Routes
@app.get("/")
async def root():
    """Serve main UI"""
    ui_file = ui_dir / "index.html"
    if ui_file.exists():
        return FileResponse(str(ui_file))
    return {"message": "NexusNet API is running"}

@app.get("/admin")
async def admin():
    """Serve admin UI"""
    admin_file = ui_dir / "admin.html"
    if admin_file.exists():
        return FileResponse(str(admin_file))
    return {"message": "Admin interface not found"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # For now, return a simple response
        # In full implementation, this would use the HiveMind system
        response = ChatResponse(
            response=f"I received your message: {request.message}. The full HiveMind system is being initialized.",
            expert="generalist",
            confidence=0.8,
            processing_time=0.1
        )
        
        # Log the query
        audit_logger.log_event("chat", {
            "message_length": len(request.message),
            "expert_used": response.expert,
            "confidence": response.confidence
        })
        
        return response
        
    except Exception as e:
        audit_logger.log_event("error", {"error": str(e), "endpoint": "/chat"})
        raise HTTPException(status_code=500, detail=str(e))

# Admin endpoints
@app.get("/admin/hardware")
async def get_hardware():
    """Get hardware information"""
    try:
        hardware = scan_hardware()
        return hardware
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/apply_autotune")
async def autotune():
    """Apply hardware auto-tuning"""
    try:
        result = apply_autotune()
        audit_logger.log_event("autotune", result)
        return result
    except Exception as e:
        audit_logger.log_event("error", {"error": str(e), "endpoint": "/admin/apply_autotune"})
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/experts")
async def get_experts():
    """Get expert configuration"""
    try:
        experts_config = load_config("experts")
        return {"experts": experts_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/experts")
async def update_experts(request: ConfigRequest):
    """Update expert configuration"""
    try:
        save_config("experts", request.config)
        audit_logger.log_event("config_update", {"type": "experts"})
        return {"success": True, "message": "Expert configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/models")
async def get_models():
    """Get available models"""
    # This would integrate with the model management system
    models = {
        "models": {
            "chat": [
                {"model_id": "microsoft/DialoGPT-medium", "size": "800MB", "type": "transformers"},
                {"model_id": "microsoft/DialoGPT-large", "size": "1.5GB", "type": "transformers"}
            ],
            "embedding": [
                {"model_id": "sentence-transformers/all-MiniLM-L6-v2", "size": "80MB", "type": "sentence_transformers"},
                {"model_id": "sentence-transformers/all-mpnet-base-v2", "size": "420MB", "type": "sentence_transformers"}
            ]
        }
    }
    return models

@app.get("/admin/hivemind")
async def get_hivemind():
    """Get HiveMind configuration"""
    try:
        hivemind_config = load_config("hivemind")
        return {"hivemind": hivemind_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/hivemind")
async def update_hivemind(request: ConfigRequest):
    """Update HiveMind configuration"""
    try:
        save_config("hivemind", request.config)
        audit_logger.log_event("config_update", {"type": "hivemind"})
        return {"success": True, "message": "HiveMind configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/keys")
async def update_keys(request: KeysRequest):
    """Update API keys (placeholder - would use secure storage)"""
    try:
        # In production, this would securely store keys
        audit_logger.log_event("keys_update", {"keys_updated": True})
        return {"success": True, "message": "API keys updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/fl")
async def get_federated_learning_status():
    """Get federated learning status"""
    return {
        "status": "idle",
        "participants": 0,
        "rounds_completed": 0,
        "last_update": None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "api": "running",
            "experts": "loaded",
            "rag": "ready",
            "hardware": "detected"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting NexusNet API server...")
    print("💡 Open http://127.0.0.1:5173 for chat interface")
    print("⚙️  Open http://127.0.0.1:5173/admin for admin panel")
    print("📚 Open http://127.0.0.1:5173/docs for API documentation")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=5173,
        reload=True,
        log_level="info"
    )
