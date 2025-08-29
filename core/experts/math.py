from .base import ExpertBase
class Math(ExpertBase):
    name="math"; triggers=['math', 'solve', 'integral', 'proof', 'equation']
    async def answer(self, prompt:str, call):
        sys=f"You are a mathematics expert. Be precise and cite as [1],[2] if evidence is provided."
        msgs=[{"role":"system","content":sys},{"role":"user","content":prompt}]
        return await call(msgs, max_tokens=512, temperature=0.2)
