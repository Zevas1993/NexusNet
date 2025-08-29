from .base import ExpertBase
class Cybersecurity(ExpertBase):
    name="cybersecurity"; triggers=['security', 'vuln', 'exploit', 'mitre', 'defense']
    async def answer(self, prompt:str, call):
        sys=f"You are a cybersecurity expert. Be precise and cite as [1],[2] if evidence is provided."
        msgs=[{"role":"system","content":sys},{"role":"user","content":prompt}]
        return await call(msgs, max_tokens=512, temperature=0.2)
