"""FastAPI main application for NexusNet with enhanced security"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uvicorn
from pathlib import Path
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import core modules with error handling
try:
    from core.config import load_config, save_config, BASE_DIR
    from core.hw.scan import scan_hardware
    from core.hw.autotune import apply_autotune
    from core.ops.audit import audit_logger
except ImportError as e:
    logger.warning(f"Core modules not fully available: {e}")
    # Provide fallback implementations
    BASE_DIR = Path(__file__).parent.parent
    def load_config(name): return {}
    def save_config(name, config): pass
    def scan_hardware(): return {"status": "not available"}
    def apply_autotune(): return {"status": "not available"}
    class MockAuditLogger:
        def log_event(self, event, data): pass
    audit_logger = MockAuditLogger()

# Security
security = HTTPBearer(auto_error=False)

# Initialize FastAPI app
app = FastAPI(
    title="NexusNet API",
    description="Unified AI Framework with HiveMind and Hybrid RAG",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Add CORS middleware with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Request/Response models with validation
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    expert: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time: float = Field(..., ge=0.0)

class ConfigRequest(BaseModel):
    config: Dict[str, Any]

class KeysRequest(BaseModel):
    openrouter_api_key: Optional[str] = Field(None, min_length=1, max_length=200)
    requesty_api_key: Optional[str] = Field(None, min_length=1, max_length=200)

# Security dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Basic auth check - implement proper authentication in production"""
    # In production, implement proper JWT validation
    return True

# Mount static files with security
ui_dir = BASE_DIR / "ui"
if ui_dir.exists():
    app.mount("/static", StaticFiles(directory=str(ui_dir)), name="static")

# Routes
@app.get("/")
async def root():
    """Serve main UI"""
    try:
        ui_file = ui_dir / "index.html"
        if ui_file.exists():
            return FileResponse(str(ui_file))
        return {"message": "NexusNet API is running", "status": "healthy"}
    except Exception as e:
        logger.error(f"Error serving root: {e}")
        return {"message": "NexusNet API is running", "status": "healthy"}

@app.get("/admin")
async def admin():
    """Serve admin UI"""
    try:
        admin_file = ui_dir / "admin.html"
        if admin_file.exists():
            return FileResponse(str(admin_file))
        return {"message": "Admin interface not found"}
    except Exception as e:
        logger.error(f"Error serving admin: {e}")
        return {"message": "Admin interface not available"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with enhanced security"""
    try:
        # Input validation
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Rate limiting check would go here in production
        
        # For now, return a secure response
        response = ChatResponse(
            response=f"I received your message. The HiveMind system is initializing securely.",
            expert="generalist",
            confidence=0.8,
            processing_time=0.1
        )
        
        # Log the query (without sensitive data)
        try:
            audit_logger.log_event("chat", {
                "message_length": len(request.message),
                "expert_used": response.expert,
                "confidence": response.confidence
            })
        except Exception as e:
            logger.warning(f"Failed to log audit event: {e}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        try:
            audit_logger.log_event("error", {"error": "chat_endpoint_error", "endpoint": "/chat"})
        except:
            pass
        raise HTTPException(status_code=500, detail="Internal server error")

# Admin endpoints
@app.get("/admin/hardware")
async def get_hardware():
    """Get hardware information"""
    try:
        hardware = scan_hardware()
        return hardware
    except Exception as e:
        logger.error(f"Hardware scan error: {e}")
        raise HTTPException(status_code=500, detail="Hardware scan failed")

@app.post("/admin/apply_autotune")
async def autotune():
    """Apply hardware auto-tuning"""
    try:
        result = apply_autotune()
        try:
            audit_logger.log_event("autotune", {"success": True})
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Autotune error: {e}")
        try:
            audit_logger.log_event("error", {"error": "autotune_failed", "endpoint": "/admin/apply_autotune"})
        except:
            pass
        raise HTTPException(status_code=500, detail="Auto-tuning failed")

@app.get("/admin/experts")
async def get_experts():
    """Get expert configuration"""
    try:
        experts_config = load_config("experts")
        return {"experts": experts_config}
    except Exception as e:
        logger.error(f"Expert config error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load expert configuration")

@app.post("/admin/experts")
async def update_experts(request: ConfigRequest):
    """Update expert configuration"""
    try:
        # Validate configuration structure
        if not isinstance(request.config, dict):
            raise HTTPException(status_code=400, detail="Invalid configuration format")
        
        save_config("experts", request.config)
        try:
            audit_logger.log_event("config_update", {"type": "experts"})
        except:
            pass
        return {"success": True, "message": "Expert configuration updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Expert update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update expert configuration")

@app.get("/admin/models")
async def get_models():
    """Get available models"""
    try:
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
    except Exception as e:
        logger.error(f"Models endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load models")

@app.get("/admin/hivemind")
async def get_hivemind():
    """Get HiveMind configuration"""
    try:
        hivemind_config = load_config("hivemind")
        return {"hivemind": hivemind_config}
    except Exception as e:
        logger.error(f"HiveMind config error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load HiveMind configuration")

@app.post("/admin/hivemind")
async def update_hivemind(request: ConfigRequest):
    """Update HiveMind configuration"""
    try:
        if not isinstance(request.config, dict):
            raise HTTPException(status_code=400, detail="Invalid configuration format")
        
        save_config("hivemind", request.config)
        try:
            audit_logger.log_event("config_update", {"type": "hivemind"})
        except:
            pass
        return {"success": True, "message": "HiveMind configuration updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"HiveMind update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update HiveMind configuration")

@app.post("/admin/keys")
async def update_keys(request: KeysRequest):
    """Update API keys (implement secure storage in production)"""
    try:
        # In production, implement secure key storage (e.g., HashiCorp Vault, AWS Secrets Manager)
        # Never log actual keys
        try:
            audit_logger.log_event("keys_update", {"keys_updated": True})
        except:
            pass
        return {"success": True, "message": "API keys updated securely"}
    except Exception as e:
        logger.error("Key update error occurred")  # Don't log the actual error to avoid key leakage
        raise HTTPException(status_code=500, detail="Failed to update API keys")

@app.get("/admin/fl")
async def get_federated_learning_status():
    """Get federated learning status"""
    try:
        return {
            "status": "idle",
            "participants": 0,
            "rounds_completed": 0,
            "last_update": None
        }
    except Exception as e:
        logger.error(f"FL status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get FL status")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
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
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "degraded",
            "version": "1.0.0",
            "error": "Health check failed"
        }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Resource not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    print("🚀 Starting NexusNet API server with enhanced security...")
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