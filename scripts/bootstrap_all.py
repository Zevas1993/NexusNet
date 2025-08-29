#!/usr/bin/env python3
print('bootstrap placeholder')


# r12.1: auto-insert repo slug into README badge if possible
def _insert_repo_slug():
    import os, re, subprocess, pathlib
    slug = os.environ.get("NEXUSNET_REPO") or ""
    # try git remote
    try:
        url = subprocess.check_output(["git","remote","get-url","origin"], stderr=subprocess.DEVNULL, text=True).strip()
        if url:
            m = re.search(r"github\.com[:/](.+/.+?)(?:\.git)?$", url)
            if m: slug = m.group(1)
    except Exception:
        pass
    if not slug:
        return False
    rd = pathlib.Path("README.md").read_text(encoding="utf-8")
    rd = rd.replace("https://github.com/OWNER/REPO", f"https://github.com/{slug}")
    pathlib.Path("README.md").write_text(rd, encoding="utf-8")
    return True

if __name__ == "__main__":
    try:
        _insert_repo_slug()
    except Exception as e:
        print("Repo badge update skipped:", e)
