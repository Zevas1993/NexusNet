import yaml, pathlib

def load_yaml(path: str):
    p=pathlib.Path(path)
    return yaml.safe_load(open(p,'r',encoding='utf-8')) if p.exists() else {}

def config():
    return load_yaml('runtime/config/rag.yaml') or {}