import json, pathlib
SRC=pathlib.Path('runtime/state/assimilation')
OUT=pathlib.Path('runtime/state/training_shards'); OUT.mkdir(parents=True,exist_ok=True)
def package_expert(expert:str):
    items=[]
    for p in sorted(SRC.glob(f"*-{expert}.json")):
        try:
            items.append(json.loads(p.read_text(encoding='utf-8')))
        except Exception:
            pass
    if not items:
        return None
    out=OUT/f"{expert}_train.jsonl"
    with open(out,'w',encoding='utf-8') as f:
        for it in items:
            row={'prompt': it.get('prompt',''),
                 'response': it.get('answer',''),
                 'meta': it.get('meta',{})}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return str(out)
