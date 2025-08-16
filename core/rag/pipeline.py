from .agent import SelfRAGAgent
class RAGPipeline:
    def __init__(self): self.agent=SelfRAGAgent(); self.indexer=self.agent.indexer
    async def answer(self,prompt:str,mode:str='auto'): return await self.agent.answer(prompt)