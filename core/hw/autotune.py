from typing import Dict, Any, List
import json, pathlib

class AutoTuner:
    def __init__(self, config_path='runtime/config/autotune.json'):
        self.config_path = pathlib.Path(config_path)
        self.profiles = self._load_profiles()
    
    def _load_profiles(self) -> Dict[str, Any]:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return self._create_default_profiles()
    
    def _create_default_profiles(self) -> Dict[str, Any]:
        return {
            'low_memory': {
                'max_model_size': '1B',
                'batch_size': 1,
                'context_length': 1024,
                'quantization': '8bit'
            },
            'balanced': {
                'max_model_size': '7B',
                'batch_size': 4,
                'context_length': 2048,
                'quantization': '4bit'
            },
            'high_performance': {
                'max_model_size': '13B',
                'batch_size': 8,
                'context_length': 4096,
                'quantization': 'none'
            }
        }
    
    def recommend_config(self, hardware_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend optimal configuration based on hardware"""
        memory_gb = hardware_specs.get('memory', {}).get('total', 0) / (1024**3)
        has_gpu = len(hardware_specs.get('gpu', [])) > 0
        
        if memory_gb < 8:
            profile = 'low_memory'
        elif memory_gb < 32 or not has_gpu:
            profile = 'balanced'
        else:
            profile = 'high_performance'
        
        config = self.profiles[profile].copy()
        config['profile'] = profile
        config['hardware_optimized'] = True
        
        return config
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(config, indent=2))