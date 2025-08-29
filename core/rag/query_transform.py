from typing import List, Dict
class SmallLLM:
    async def complete_async(self, prompt: str, max_tokens: int = 128, temperature: float = 0.0):
        return prompt.split("\n")[-1][:128]
class QueryTransforms:
    def __init__(self, llm_small=None, enable_hyde=True, n_rewrites=4, max_chars=220, max_embeddings=64):
        self.llm = llm_small or SmallLLM()
        self.enable_hyde, self.n, self.maxc, self.max_embeddings = enable_hyde, n_rewrites, max_chars, max_embeddings
    async def rewrites(self, q: str) -> List[str]:
        styles = ["concise","expanded detail","entity focus","time focus"]
        tpl = "Rewrite the query in {style}. Keep under {n} chars.\nQ: {q}\nA:"
        outs = [ (await self.llm.complete_async(tpl.format(style=s, n=self.maxc, q=q))).strip() for s in styles[:self.n] ]
        return list(dict.fromkeys([q]+[o for o in outs if o]))
    async def hyde(self, q: str) -> str | None:
        if not self.enable_hyde: return None
        out = (await self.llm.complete_async(f"Write a 2-4 sentence hypothetical answer.\nQ: {q}\nHypothesis:")).strip()
        return out[:512] if out else None
    async def expand(self, q: str) -> Dict[str, list[str]]:
        R = await self.rewrites(q); H = await self.hyde(q)
        items = (R + ([H] if H else []))[: self.max_embeddings]
        return {"queries": R, "hyde": [H] if H else [], "embed_items": items}
