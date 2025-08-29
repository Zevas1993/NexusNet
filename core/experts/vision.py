from .base import ExpertBase
class Vision(ExpertBase):
    name="vision"; triggers=['image', 'vision', 'ocr', 'multimodal']
    async def answer(self, prompt:str, call):
        sys=f"You are a vision/multimodal expert. Be precise and cite as [1],[2] if evidence is provided."
        msgs=[{"role":"system","content":sys},{"role":"user","content":prompt}]
        return await call(msgs, max_tokens=512, temperature=0.2)
