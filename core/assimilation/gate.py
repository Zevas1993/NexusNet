from typing import Dict, Any

class ReadinessGate:
    def __init__(self, min_samples=100, quality_threshold=0.7):
        self.min_samples = min_samples
        self.quality_threshold = quality_threshold
    
    def assess(self, batch: list[Dict[str, Any]]) -> Dict[str, Any]:
        if len(batch) < self.min_samples:
            return {'ready': False, 'reason': 'insufficient_data', 'count': len(batch)}
        
        # Simple quality check (can be enhanced)
        valid_count = sum(1 for item in batch if item.get('data', {}).get('text', '').strip())
        quality = valid_count / len(batch) if batch else 0.0
        
        if quality < self.quality_threshold:
            return {'ready': False, 'reason': 'low_quality', 'quality': quality}
        
        return {'ready': True, 'quality': quality, 'count': len(batch)}