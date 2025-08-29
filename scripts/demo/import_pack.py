
#!/usr/bin/env python3
from __future__ import annotations
import shutil, os, glob, pathlib, subprocess

def main():
    os.makedirs("data/corpus/demo", exist_ok=True)
    for p in glob.glob("data/demo_pack/*.txt"):
        shutil.copy(p, "data/corpus/demo/")
    try:
        subprocess.run(["python","scripts/rag/watch_ingest.py"], check=False)
    except Exception:
        pass
    print("Demo pack imported.")
if __name__ == "__main__":
    main()
