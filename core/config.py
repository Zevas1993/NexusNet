"""Core configuration for NexusNet with enhanced security"""
from pathlib import Path
import os
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Base paths with validation
try:
    BASE_DIR = Path(__file__).parent.parent
    RUNTIME_DIR = BASE_DIR / "runtime"
    CONFIG_DIR = RUNTIME_DIR / "config"
    STATE_DIR = RUNTIME_DIR / "state"
    MODELS_DIR = RUNTIME_DIR / "models"
    
    # Ensure directories exist with proper permissions
    for dir_path in [RUNTIME_DIR, CONFIG_DIR, STATE_DIR, MODELS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True, mode=0o755)
        
except Exception as e:
    logger.error(f"Failed to initialize directories: {e}")
    # Fallback to safer defaults
    BASE_DIR = Path.cwd()
    RUNTIME_DIR = BASE_DIR / "runtime"
    CONFIG_DIR = RUNTIME_DIR / "config"
    STATE_DIR = RUNTIME_DIR / "state"
    MODELS_DIR = RUNTIME_DIR / "models"

# API Keys with validation
def get_api_key(key_name: str) -> Optional[str]:
    """Safely retrieve API key from environment"""
    key = os.getenv(key_name)
    if key and len(key.strip()) > 0:
        return key.strip()
    return None

OPENROUTER_API_KEY = get_api_key("OPENROUTER_API_KEY")
REQUESTY_API_KEY = get_api_key("REQUESTY_API_KEY")
VLLM_URL = os.getenv("VLLM_URL", "http://127.0.0.1:8000/v1")

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# Security settings
MAX_CONFIG_SIZE = 1024 * 1024  # 1MB max config file size
ALLOWED_CONFIG_KEYS = {
    "experts", "rag", "hivemind", "assimilation", "training_criteria"
}

# Default configurations with secure defaults
DEFAULT_EXPERT_CONFIG = {
    "enabled": True,
    "temperature": 0.7,
    "max_tokens": 2048,
    "confidence_threshold": 0.6,
    "rate_limit": 60  # requests per minute
}

DEFAULT_RAG_CONFIG = {
    "chunk_size": 512,
    "chunk_overlap": 50,
    "top_k": 5,
    "rerank_top_k": 3,
    "use_colbert": True,
    "use_bm25": True,
    "use_dense": True,
    "max_query_length": 1000
}

DEFAULT_HIVEMIND_CONFIG = {
    "consensus_method": "weighted_vote",
    "min_experts": 3,
    "max_experts": 10,
    "confidence_weight": 0.4,
    "diversity_weight": 0.3,
    "accuracy_weight": 0.3,
    "timeout_seconds": 30
}

def validate_config_name(config_name: str) -> bool:
    """Validate configuration name for security"""
    if not config_name or not isinstance(config_name, str):
        return False
    
    # Check for path traversal attempts
    if ".." in config_name or "/" in config_name or "\\" in config_name:
        logger.warning(f"Invalid config name attempted: {config_name}")
        return False
    
    # Check if it's an allowed config type
    if config_name not in ALLOWED_CONFIG_KEYS:
        logger.warning(f"Unauthorized config access attempted: {config_name}")
        return False
    
    return True

def load_config(config_name: str) -> Dict[str, Any]:
    """Load configuration from yaml file with security validation"""
    if not validate_config_name(config_name):
        logger.error(f"Invalid config name: {config_name}")
        return {}
    
    try:
        config_path = CONFIG_DIR / f"{config_name}.yaml"
        
        # Check if file exists and is readable
        if not config_path.exists():
            logger.info(f"Config file not found, using defaults: {config_name}")
            defaults = {
                "experts": DEFAULT_EXPERT_CONFIG,
                "rag": DEFAULT_RAG_CONFIG,
                "hivemind": DEFAULT_HIVEMIND_CONFIG
            }
            return defaults.get(config_name, {})
        
        # Check file size for security
        if config_path.stat().st_size > MAX_CONFIG_SIZE:
            logger.error(f"Config file too large: {config_name}")
            return {}
        
        # Load and validate YAML
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        if not isinstance(config, dict):
            logger.error(f"Invalid config format: {config_name}")
            return {}
            
        logger.info(f"Successfully loaded config: {config_name}")
        return config
        
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error for {config_name}: {e}")
        return {}
    except PermissionError:
        logger.error(f"Permission denied reading config: {config_name}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading config {config_name}: {e}")
        return {}

def save_config(config_name: str, config: Dict[str, Any]) -> bool:
    """Save configuration to yaml file with security validation"""
    if not validate_config_name(config_name):
        logger.error(f"Invalid config name: {config_name}")
        return False
    
    if not isinstance(config, dict):
        logger.error(f"Invalid config data type: {type(config)}")
        return False
    
    try:
        config_path = CONFIG_DIR / f"{config_name}.yaml"
        
        # Create backup if file exists
        if config_path.exists():
            backup_path = config_path.with_suffix('.yaml.backup')
            config_path.rename(backup_path)
        
        # Write new config
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        # Set secure permissions
        config_path.chmod(0o644)
        
        logger.info(f"Successfully saved config: {config_name}")
        return True
        
    except PermissionError:
        logger.error(f"Permission denied writing config: {config_name}")
        return False
    except Exception as e:
        logger.error(f"Error saving config {config_name}: {e}")
        return False

def get_secure_config_path(filename: str) -> Optional[Path]:
    """Get a secure path within the config directory"""
    if not filename or ".." in filename or "/" in filename:
        return None
    
    return CONFIG_DIR / filename

# Initialize logging configuration
def setup_logging():
    """Setup secure logging configuration"""
    log_level = logging.DEBUG if DEBUG else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(RUNTIME_DIR / 'app.log') if RUNTIME_DIR.exists() else logging.NullHandler()
        ]
    )

# Initialize logging on import
setup_logging()