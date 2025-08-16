"""Core configuration for NexusNet"""
from pathlib import Path
import os
from typing import Dict, Any
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
RUNTIME_DIR = BASE_DIR / "runtime"
CONFIG_DIR = RUNTIME_DIR / "config"
STATE_DIR = RUNTIME_DIR / "state"
MODELS_DIR = RUNTIME_DIR / "models"

# Ensure directories exist
for dir_path in [RUNTIME_DIR, CONFIG_DIR, STATE_DIR, MODELS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
REQUESTY_API_KEY = os.getenv("REQUESTY_API_KEY")
VLLM_URL = os.getenv("VLLM_URL", "http://127.0.0.1:8000/v1")

# Default configurations
DEFAULT_EXPERT_CONFIG = {
    "enabled": True,
    "temperature": 0.7,
    "max_tokens": 2048,
    "confidence_threshold": 0.6
}

DEFAULT_RAG_CONFIG = {
    "chunk_size": 512,
    "chunk_overlap": 50,
    "top_k": 5,
    "rerank_top_k": 3,
    "use_colbert": True,
    "use_bm25": True,
    "use_dense": True
}

DEFAULT_HIVEMIND_CONFIG = {
    "consensus_method": "weighted_vote",
    "min_experts": 3,
    "confidence_weight": 0.4,
    "diversity_weight": 0.3,
    "accuracy_weight": 0.3
}

def load_config(config_name: str) -> Dict[str, Any]:
    """Load configuration from yaml file"""
    config_path = CONFIG_DIR / f"{config_name}.yaml"
    
    if not config_path.exists():
        # Return default config
        defaults = {
            "experts": DEFAULT_EXPERT_CONFIG,
            "rag": DEFAULT_RAG_CONFIG,
            "hivemind": DEFAULT_HIVEMIND_CONFIG
        }
        return defaults.get(config_name, {})
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def save_config(config_name: str, config: Dict[str, Any]) -> None:
    """Save configuration to yaml file"""
    config_path = CONFIG_DIR / f"{config_name}.yaml"
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
