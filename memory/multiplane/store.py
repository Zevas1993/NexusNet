
import json, os, time
PLANES = ["conceptual","temporal","procedural","imaginal","social","ethical","metacognitive"]
class Memory:
    def __init__(self, root='data/memory'):
        self.root=root; os.makedirs(root, exist_ok=True)
        for p in PLANES: os.makedirs(os.path.join(root,p), exist_ok=True)
    def put(self, plane: str, content: dict):
        path=os.path.join(self.root,plane,f"{int(time.time()*1000)}.json")
        with open(path,'w') as f: json.dump(content,f); return path
    def scan(self, plane: str, limit=50):
        p=os.path.join(self.root,plane); files=sorted(os.listdir(p))[-limit:]
        return [json.load(open(os.path.join(p,x))) for x in files]
