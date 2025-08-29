
import os, shutil
def ingest_curated(curated_path: str, inbox: str = 'data/assimilation/inbox'):
    os.makedirs(inbox, exist_ok=True)
    dst = os.path.join(inbox, os.path.basename(curated_path))
    shutil.copyfile(curated_path, dst)
    return dst
