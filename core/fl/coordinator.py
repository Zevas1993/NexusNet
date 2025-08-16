from typing import List, Dict, Any
import numpy as np

class FLCoordinator:
    def __init__(self, num_rounds: int = 10, min_participants: int = 2):
        self.num_rounds = num_rounds
        self.min_participants = min_participants
        self.participants: Dict[str, Any] = {}
        self.global_model = None
        self.round_number = 0
    
    def register_participant(self, participant_id: str, metadata: Dict[str, Any]):
        """Register a new participant in the federation"""
        self.participants[participant_id] = {
            'id': participant_id,
            'metadata': metadata,
            'active': True,
            'last_seen': None
        }
    
    def aggregate_updates(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate model updates from participants using FedAvg"""
        if len(updates) < self.min_participants:
            raise ValueError(f"Insufficient participants: {len(updates)} < {self.min_participants}")
        
        # Simple FedAvg implementation
        total_samples = sum(update['num_samples'] for update in updates)
        
        aggregated = {}
        for update in updates:
            weight = update['num_samples'] / total_samples
            for param_name, param_value in update['parameters'].items():
                if param_name not in aggregated:
                    aggregated[param_name] = np.zeros_like(param_value)
                aggregated[param_name] += weight * param_value
        
        return {
            'round': self.round_number,
            'parameters': aggregated,
            'num_participants': len(updates)
        }
    
    def start_round(self) -> Dict[str, Any]:
        """Start a new federated learning round"""
        self.round_number += 1
        return {
            'round': self.round_number,
            'global_model': self.global_model,
            'participants': list(self.participants.keys())
        }