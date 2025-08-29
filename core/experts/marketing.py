from .base import ExpertBase
class Marketing(ExpertBase):
    name="marketing"; triggers=['marketing', 'copy', 'seo', 'campaign', 'ad']
    async def answer(self, prompt:str, call):
        sys=f"You are a marketing expert. Be precise and cite as [1],[2] if evidence is provided."
        msgs=[{"role":"system","content":sys},{"role":"user","content":prompt}]
        return await call(msgs, max_tokens=512, temperature=0.2)
