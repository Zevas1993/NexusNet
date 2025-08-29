
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..core.inference import InferenceSelector
from ..core.memory import ChatMemoryStore
from ..core.router import ExpertRouter
from ..core.config import settings

router = APIRouter()

selector = InferenceSelector()
router_state = {"router": ExpertRouter()}
memory = ChatMemoryStore()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    model_hint: Optional[str] = None

@router.post("/chat")
def chat(req: ChatRequest):
    # Persist chat memory per session
    memory.append(req.session_id, [{"role": m.role, "content": m.content} for m in req.messages])

    # Route to expert(s) if needed
    expert = router_state["router"].route(req.messages)

    # Select backend
    backend = selector.select_backend(model_hint=req.model_hint)

    # Generate response
    try:
        text = backend.generate(req.messages, expert_hint=expert)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

    # Save assistant reply to memory
    memory.append(req.session_id, [{"role":"assistant","content": text}])
    return {"reply": text, "expert": expert, "backend": backend.name}
