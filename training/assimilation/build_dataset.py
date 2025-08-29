
import os, glob, json, random
def build(inbox='data/assimilation/inbox', out_path='data/assimilation/dataset.jsonl', shuffle=True):
    files = glob.glob(os.path.join(inbox,'*.jsonl')); rows=[]
    for fp in files: rows += [json.loads(x) for x in open(fp,encoding='utf-8')]
    if shuffle: random.shuffle(rows)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path,'w',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False)+'\n')
    return {'examples': len(rows), 'path': out_path}
