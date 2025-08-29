
#!/usr/bin/env python3
import argparse, os, shutil, yaml, json

def merge_yaml(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k,v in b.items():
            out[k] = merge_yaml(out.get(k), v)
        return out
    return b if b is not None else a

def load_yaml(path):
    try:
        with open(path,"r",encoding="utf-8") as f: return yaml.safe_load(f) or {}
    except Exception:
        return {}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True, help="Path to old repo root")
    ap.add_argument("--new", default=".", help="Path to new repo root")
    args = ap.parse_args()

    # candidates
    olds = {
        "rag.yaml": os.path.join(args.old, "runtime/config/rag.yaml"),
        "experts.yaml": os.path.join(args.old, "runtime/config/experts.yaml"),
        "providers.yaml": os.path.join(args.old, "runtime/config/providers.yaml"),
        "train.yaml": os.path.join(args.old, "runtime/config/train.yaml"),
        "federated.yaml": os.path.join(args.old, "runtime/config/federated.yaml"),
        "secrets.json": os.path.join(args.old, "runtime/config/secrets.json"),
    }
    news = {k: os.path.join(args.new, "runtime/config", k) for k in olds.keys()}

    for key in ["rag.yaml","experts.yaml","providers.yaml","train.yaml","federated.yaml"]:
        if os.path.exists(olds[key]):
            old_yaml = load_yaml(olds[key])
            new_yaml = load_yaml(news[key])
            merged = merge_yaml(new_yaml, old_yaml)
            os.makedirs(os.path.dirname(news[key]), exist_ok=True)
            with open(news[key], "w", encoding="utf-8") as f:
                yaml.safe_dump(merged, f, sort_keys=False)
            print(f"Merged {key}")

    # secrets: do not merge blindly; copy if destination empty
    if os.path.exists(olds["secrets.json"]) and not os.path.exists(news["secrets.json"]):
        shutil.copy2(olds["secrets.json"], news["secrets.json"])
        print("Copied secrets.json (destination was missing).")
    else:
        print("Skipped secrets.json (destination exists).")

if __name__ == "__main__":
    main()
