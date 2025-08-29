
#!/usr/bin/env python3
from __future__ import annotations
import os, time, glob, hashlib
from pathlib import Path
from temporal import tkg
from temporal.atomic_extractor import extract_facts

STATE="runtime/state/ingest.hash"
os.makedirs("runtime/state", exist_ok=True)

def digest():
    h=hashlib.sha256()
    for p in glob.glob("data/corpus/**/*.txt", recursive=True):
        with open(p,"rb") as f: h.update(f.read())
    return h.hexdigest()

def ingest():
    for p in glob.glob("data/corpus/**/*.txt", recursive=True):
        try:
            txt = Path(p).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # naive: each line -> fact about file contains text
        facts=extract_facts(txt)
        if facts:
            for f in facts:
                tkg.upsert_fact(f['s'], f['p'], f['o'], p, int(time.time()-86400), int(time.time()+10*365*86400))
        else:
            tkg.upsert_fact(subj=p, pred='contains', obj=txt[:40], source=p, valid_from=int(time.time()-86400), valid_to=int(time.time()+10*365*86400))

def main():
    cur = digest()
    prev = Path(STATE).read_text(encoding="utf-8") if Path(STATE).exists() else ""
    if cur != prev:
        ingest()
        Path(STATE).write_text(cur, encoding="utf-8")
        print("Indexed changes.")
    else:
        print("No changes.")
if __name__ == "__main__":
    main()
