
from huggingface_hub import snapshot_download
import os
model = os.environ.get("NEXUSNET_MODEL_ID","TinyLlama/TinyLlama-1.1B-Chat-v1.0")
print("Downloading:", model)
snapshot_download(repo_id=model, local_dir="models/"+model.replace('/','__'), ignore_patterns=["*.safetensors.index.json"])
print("Done")
