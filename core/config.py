import yaml, json, pathlib
def _load(path): p=pathlib.Path(path); return yaml.safe_load(open(p,'r',encoding='utf-8')) if p.exists() else {}
def cfg_rag(): return _load('runtime/config/rag.yaml') or {}
def cfg_experts(): return _load('runtime/config/experts.yaml') or {}
def cfg_hm(): return _load('runtime/config/hivemind.yaml') or {}
def cfg_assim(): return _load('runtime/config/assimilation.yaml') or {}
def paths():
    p=pathlib.Path('runtime/config/paths.json')
    return json.loads(p.read_text()) if p.exists() else {"model_dir":"runtime/models"}
