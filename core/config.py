import yaml, pathlib, os

def load_yaml(path: str):
    p = pathlib.Path(path)
    return yaml.safe_load(open(p, 'r', encoding='utf-8')) if p.exists() else {}

def config():
    return load_yaml('runtime/config/rag.yaml') or {}

def hivemind_config():
    return load_yaml('runtime/config/hivemind.yaml') or {}

def experts_config():
    return load_yaml('runtime/config/experts.yaml') or {}

def paths_config():
    import json
    p = pathlib.Path('runtime/config/paths.json')
    return json.loads(p.read_text()) if p.exists() else {}

def env_var(key: str, default=None):
    return os.getenv(key, default)