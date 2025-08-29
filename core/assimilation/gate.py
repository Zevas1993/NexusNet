import httpx, pathlib
from core.config import cfg_assim
def readiness(metrics: dict, interactions: int) -> bool:
    thr = cfg_assim().get("thresholds",{})
    return interactions >= thr.get("min_interactions_per_expert",50) and metrics.get("ais_coverage",0.0) >= thr.get("min_ais_coverage",0.8) and metrics.get("citation_rate",0.0) >= thr.get("min_citation_rate",0.8)
async def poll_leaderboards() -> dict:
    out={}
    for lb in cfg_assim().get("leaderboards",[]):
        try:
            async with httpx.AsyncClient(timeout=5) as c:
                r=await c.get(lb['url']); out[lb['name']]=r.status_code
        except Exception:
            out[lb['name']]='unreachable'
    return out
def notify(msg: str):
    pathlib.Path("runtime/state/notify.log").write_text(msg, encoding="utf-8")
