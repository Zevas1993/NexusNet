from .base import ExpertBase
class Medical(ExpertBase):
    name="medical"; triggers=['medical', 'diagnosis', 'drug', 'treatment']
    async def answer(self, prompt:str, call):
        sys=f"You are a medical expert. Be precise and cite as [1],[2] if evidence is provided."
        msgs=[{"role":"system","content":sys},{"role":"user","content":prompt}]
        return await call(msgs, max_tokens=512, temperature=0.2)
