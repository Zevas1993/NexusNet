from .base import ExpertBase
class Search(ExpertBase):
    name="search"; triggers=['search', 'retrieval', 'ranking', 'query']
    async def answer(self, prompt:str, call):
        sys=f"You are a information retrieval expert. Be precise and cite as [1],[2] if evidence is provided."
        msgs=[{"role":"system","content":sys},{"role":"user","content":prompt}]
        return await call(msgs, max_tokens=512, temperature=0.2)
