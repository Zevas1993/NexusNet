from __future__ import annotations

from pathlib import Path


class GGUFCatalog:
    def __init__(self, inference_config: dict):
        self.inference_config = inference_config

    def entries(self) -> list[dict]:
        model_path = self.inference_config.get("llama_cpp", {}).get("model_path", "models/tiny/tinyllama.gguf")
        return [
            {
                "status_label": "STRONG ACCEPTED DIRECTION",
                "model_path": model_path,
                "exists": Path(model_path).exists(),
                "format": "gguf",
                "runtime_name": "llama.cpp",
                "safe_mode": True,
            }
        ]
