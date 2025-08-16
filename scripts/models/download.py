# Model Download Script
import os, sys, pathlib
try: import huggingface_hub
except ImportError: print("pip install huggingface_hub"); sys.exit(1)

def download_model(model_name: str, model_type: str = "transformers"):
    """Download model to local cache"""
    cache_dir = pathlib.Path("runtime/models")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    if model_type == "gguf":
        # Download GGUF models
        filename = f"{model_name.split('/')[-1]}.gguf"
        try:
            path = huggingface_hub.hf_hub_download(
                repo_id=model_name,
                filename=filename,
                cache_dir=str(cache_dir)
            )
            print(f"Downloaded: {path}")
            return path
        except Exception as e:
            print(f"Failed to download {model_name}: {e}")
            return None
    else:
        # Download transformers models
        try:
            path = huggingface_hub.snapshot_download(
                repo_id=model_name,
                cache_dir=str(cache_dir)
            )
            print(f"Downloaded: {path}")
            return path
        except Exception as e:
            print(f"Failed to download {model_name}: {e}")
            return None

if __name__ == "__main__":
    import yaml
    
    # Load model map
    model_map_path = pathlib.Path("scripts/models/model_map.yaml")
    if not model_map_path.exists():
        print("Model map not found")
        sys.exit(1)
    
    with open(model_map_path) as f:
        models = yaml.safe_load(f)
    
    # Download recommended models
    for category, model_list in models.items():
        print(f"\nDownloading {category} models...")
        for model in model_list.get("recommended", []):
            download_model(model["name"], model.get("type", "transformers"))