
import yaml, os, json
from dataclasses import dataclass, asdict

@dataclass
class Objective:
    name: str
    weight: float

@dataclass
class QESConfig:
    enabled: bool = True
    interval_hours: int = 24
    budget: dict = None
    objectives: list = None
    search_space: dict = None
    safety: dict = None
    persist_dir: str = "runtime/qes"

def load_config(path:str="runtime/config/qes.yaml")->QESConfig:
    with open(path,"r",encoding="utf-8") as f:
        cfg=yaml.safe_load(f) or {}
    obj=[Objective(**o) for o in (cfg.get("objectives") or [])]
    return QESConfig(enabled=cfg.get("enabled",True),
                     interval_hours=cfg.get("interval_hours",24),
                     budget=cfg.get("budget") or {},
                     objectives=obj,
                     search_space=cfg.get("search_space") or {},
                     safety=cfg.get("safety") or {},
                     persist_dir=cfg.get("persist_dir","runtime/qes"))
