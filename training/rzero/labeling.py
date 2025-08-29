
from typing import List, Dict, Tuple
from collections import Counter
import os, json, time
def majority_vote(samples: List[str]) -> Tuple[str, int]:
    c = Counter(samples); label, votes = c.most_common(1)[0]; return label, votes
def filter_informative_band(items: List[Dict], low: int, high: int) -> List[Dict]:
    curated = []
    for it in items:
        if not it.get('format_ok', True): continue
        label, votes = majority_vote(it['samples'])
        if low <= votes <= high:
            curated.append({'question': it['question'], 'label': label, 'votes': votes, 'samples': it['samples']})
    return curated
def write_curated_jsonl(curated: List[Dict], out_dir: str, experiment: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    fname = f"curated-{experiment}-{int(time.time())}.jsonl"; path = os.path.join(out_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        for ex in curated: f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    return path
