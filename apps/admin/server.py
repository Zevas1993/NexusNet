
from fastapi import FastAPI
from apps.admin.routes.rzero_routes import router as rzero_router
from apps.admin.routes.metrics_routes import router as metrics_router
from apps.admin.routes.eval_routes import router as eval_router
from apps.admin.routes.assimilation_routes import router as assimilation_router
app = FastAPI(title="NexusNet Admin API")
app.include_router(rzero_router); app.include_router(metrics_router)
app.include_router(eval_router); app.include_router(assimilation_router)
@app.get("/health")
def health(): return {"ok": True}
