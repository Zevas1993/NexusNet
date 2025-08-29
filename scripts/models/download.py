import argparse, os, pathlib, yaml
from huggingface_hub import snapshot_download
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dest', default='runtime/models')
    ap.add_argument('--only', choices=['cpu_gguf','gpu_transformers','all'], default='all')
    ap.add_argument('--file','-f', default='scripts/models/model_map.yaml')
    args=ap.parse_args()
    dest=pathlib.Path(args.dest); dest.mkdir(parents=True, exist_ok=True)
    cfg=yaml.safe_load(open(args.file,'r',encoding='utf-8'))
    def pull(model_id):
        print('Pulling', model_id)
        snapshot_download(repo_id=model_id, local_dir=dest / model_id.replace('/','__'), local_dir_use_symlinks=False, ignore_patterns=["*.safetensors","*.bin"] if "GGUF" in model_id.upper() else None)
    if args.only in ('cpu_gguf','all'):
        for mid,_ in cfg.get('cpu_gguf',{}).items(): pull(mid)
    if args.only in ('gpu_transformers','all'):
        for mid,_ in cfg.get('gpu_transformers',{}).items(): pull(mid)
    print('Done.')
if __name__=='__main__': main()
