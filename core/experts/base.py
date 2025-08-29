class ExpertBase:
    name="base"; triggers=[]
    def wants(self, prompt:str)->float:
        p=prompt.lower()
        return 1.0 if any(t in p for t in self.triggers) else 0.2
    async def answer(self, prompt:str, call): raise NotImplementedError
