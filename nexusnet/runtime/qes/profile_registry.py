from __future__ import annotations

from pathlib import Path

from nexus.config import load_yaml_file


class QESProfileRegistry:
    def __init__(self, config_dir: Path):
        self.quant_path = config_dir / "quant_profile.yaml"
        self.qes_path = config_dir / "qes_policy.yaml"
        self.quant_profile = load_yaml_file(self.quant_path, {})
        self.qes_policy = load_yaml_file(self.qes_path, {})

    def summary(self) -> dict:
        return {
            "status_label": "LOCKED CANON",
            "quant_profile": self.quant_profile,
            "qes_policy": self.qes_policy,
        }
