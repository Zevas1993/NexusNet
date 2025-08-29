import json, pathlib, time
BASE=pathlib.Path('runtime/state/assimilation'); BASE.mkdir(parents=True,exist_ok=True)

def log_interaction(expert,prompt,answer,meta=None):
    t=int(time.time()*1000); p=BASE/f"{t}-{expert}.json"; p.write_text(json.dumps({'expert':expert,'prompt':prompt,'answer':answer,'meta':meta or {}}, ensure_ascii=False, indent=2), encoding='utf-8'); return str(p)
