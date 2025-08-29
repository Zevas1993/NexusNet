from .base import ExpertBase
class Education(ExpertBase):
    name="education"; triggers=['teach', 'tutor', 'explain', 'lesson']
    async def answer(self, prompt:str, call):
        sys=f"You are a education expert. Be precise and cite as [1],[2] if evidence is provided."
        msgs=[{"role":"system","content":sys},{"role":"user","content":prompt}]
        return await call(msgs, max_tokens=512, temperature=0.2)
