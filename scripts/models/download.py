#!/usr/bin/env python3
"""Download models based on model_map.yaml"""
import yaml
import argparse
import subprocess
import sys
from pathlib import Path

def load_model_map():
    """Load model configuration"""
    script_dir = Path(__file__).parent
    model_map_path = script_dir / "model_map.yaml"
    
    with open(model_map_path, 'r') as f:
        return yaml.safe_load(f)

def download_model(model_info):
    """Download a single model"""
    model_id = model_info['model_id']
    model_type = model_info['type']
    
    print(f"Downloading {model_id} ({model_info['size']})...")
    
    if model_type == 'transformers':
        cmd = [sys.executable, '-c', f"from transformers import AutoModel, AutoTokenizer; AutoModel.from_pretrained('{model_id}'); AutoTokenizer.from_pretrained('{model_id}')"]
    elif model_type == 'sentence_transformers':
        cmd = [sys.executable, '-c', f"from sentence_transformers import SentenceTransformer; SentenceTransformer('{model_id}')"]
    else:
        print(f"Unknown model type: {model_type}")
        return False
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✓ Downloaded {model_id}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to download {model_id}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Download models')
    parser.add_argument('--only', choices=['chat', 'embedding', 'all'], default='all',
                       help='Download only specific type of models')
    args = parser.parse_args()
    
    models = load_model_map()
    
    if args.only == 'all':
        to_download = []
        for category in models['models'].values():
            to_download.extend(category)
    else:
        to_download = models['models'][args.only]
    
    print(f"Downloading {len(to_download)} models...")
    
    success_count = 0
    for model_info in to_download:
        if download_model(model_info):
            success_count += 1
    
    print(f"\nDownload complete: {success_count}/{len(to_download)} successful")

if __name__ == '__main__':
    main()
