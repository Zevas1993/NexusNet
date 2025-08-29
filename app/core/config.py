
import os, yaml
from pydantic import BaseModel
from typing import Any, Dict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_ROOT = os.path.join(ROOT, "runtime", "config")

def _read_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}

def save_yaml(path, data):
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)

class Settings(BaseModel):
    inference: Dict[str, Any] = {}
    experts: Dict[str, Any] = {}
    planes: Dict[str, Any] = {}
    router: Dict[str, Any] = {}
    rag: Dict[str, Any] = {}
    qes: Dict[str, Any] = {}
    federated: Dict[str, Any] = {}

settings = Settings()

def load_all_configs():
    settings.inference = _read_yaml(os.path.join(CONFIG_ROOT, "inference.yaml"))
    settings.experts = _read_yaml(os.path.join(CONFIG_ROOT, "experts.yaml"))
    settings.planes = _read_yaml(os.path.join(CONFIG_ROOT, "planes.yaml"))
    settings.router = _read_yaml(os.path.join(CONFIG_ROOT, "router.yaml"))
    settings.rag = _read_yaml(os.path.join(CONFIG_ROOT, "rag.yaml"))
    settings.qes = _read_yaml(os.path.join(CONFIG_ROOT, "qes_policy.yaml"))
    settings.federated = _read_yaml(os.path.join(CONFIG_ROOT, "federated.yaml"))
    return settings
