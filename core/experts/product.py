from .base import ExpertBase
class Product(ExpertBase):
    name="product"; triggers=['product', 'requirements', 'roadmap', 'feature', 'spec']
    async def answer(self, prompt:str, call):
        sys=f"You are a product management expert. Be precise and cite as [1],[2] if evidence is provided."
        msgs=[{"role":"system","content":sys},{"role":"user","content":prompt}]
        return await call(msgs, max_tokens=512, temperature=0.2)
