
#!/usr/bin/env python3
from __future__ import annotations
import glob, json, os, time
from services.sessions_sqlite import save

def main():
    for p in glob.glob("data/sessions/*.json"):
        try:
            with open(p,"r",encoding="utf-8") as f:
                d=json.load(f)
            sid=os.path.splitext(os.path.basename(p))[0]
            save(sid, d)
        except Exception as e:
            print("skip", p, e)
    print("done")
if __name__ == "__main__":
    main()
