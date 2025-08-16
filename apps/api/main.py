from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from core.rag.pipeline import RAGPipeline

app = FastAPI(title="NexusNet")
PIPE = RAGPipeline()

@app.get("/", response_class=HTMLResponse)
def home():
    return open("ui/index.html","r",encoding="utf-8").read()

class IndexIn(BaseModel):
    docs: list[dict]

class QueryIn(BaseModel):
    prompt: str
    mode: str | None = "auto"

@app.post("/rag/index")
async def rag_index(inp: IndexIn):
    PIPE.indexer.add_documents(inp.docs); return {"ok": True, "added": len(inp.docs)}

@app.post("/rag/query")
async def rag_query(inp: QueryIn):
    try:
        out = await PIPE.answer(inp.prompt, mode=inp.mode or "auto")
        return JSONResponse(out)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)