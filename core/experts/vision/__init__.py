from .tools import TOOLBOX
from .prompts import SYSTEM_PROMPT
class Expert:
    def __init__(self, name="vision"):
        self.name=name
    def system_prompt(self): return SYSTEM_PROMPT
    def tools(self): return TOOLBOX
    def plan(self, query:str)->str:
        return "[" + self.name + "] analyze -> search -> draft -> verify"
