from .base import ExpertBase
class Design(ExpertBase):
    name="design"; triggers=['design', 'ux', 'ui', 'layout', 'color']
    async def answer(self, prompt:str, call):
        sys=f"You are a design/UX expert. Be precise and cite as [1],[2] if evidence is provided."
        msgs=[{"role":"system","content":sys},{"role":"user","content":prompt}]
        return await call(msgs, max_tokens=512, temperature=0.2)
