import time, os
from core.providers.openrouter import OpenRouterAdapter
from core.providers.requesty import RequestyAdapter
class TeacherGate:
    def __init__(self, budget_per_hour_cents=50, max_calls_per_query=2, prov_cfg=None):
        self.budget_cents = budget_per_hour_cents; self.max_calls = max_calls_per_query
        self.usage = {'cents': 0.0, 'ts': time.time()}; self.adapters = []
        prov_cfg = prov_cfg or {}
        if prov_cfg.get('openrouter',{}).get('enabled',True) and os.getenv('OPENROUTER_API_KEY'):
            self.adapters.append(OpenRouterAdapter(model=prov_cfg.get('openrouter',{}).get('model','openrouter/auto')))
        if prov_cfg.get('requesty',{}).get('enabled',True) and os.getenv('REQUESTY_API_KEY'):
            self.adapters.append(RequestyAdapter(model=prov_cfg.get('requesty',{}).get('model','gpt-4o-mini')))
    def _under_budget(self):
        now=time.time()
        if now - self.usage['ts'] > 3600: self.usage={'cents':0.0,'ts':now}
        return self.usage['cents'] < self.budget_cents
    def should_consult(self, signal) -> bool:
        if not self.adapters or not self._under_budget(): return False
        if signal.get('calls',0) >= self.max_calls: return False
        return signal.get('coverage',0.0) < 0.8 or signal.get('hard',True)
    async def complete(self, prompt: str, **kw):
        for a in self.adapters:
            try:
                out = await a.complete_async([{'role':'user','content':prompt}], **kw)
                self.usage['cents'] += 2
                return out.strip()
            except Exception: continue
        return None
