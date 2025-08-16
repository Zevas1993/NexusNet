import secrets, hashlib
from typing import Dict, List, Any

class SecureAggregator:
    def __init__(self, num_parties: int):
        self.num_parties = num_parties
        self.masks: Dict[int, bytes] = {}
    
    def generate_pairwise_masks(self, party_id: int) -> Dict[int, bytes]:
        """Generate pairwise masks for secure aggregation"""
        masks = {}
        for other_party in range(self.num_parties):
            if other_party != party_id:
                # Generate a shared secret between party_id and other_party
                seed = f"{min(party_id, other_party)}_{max(party_id, other_party)}"
                mask = hashlib.sha256(seed.encode()).digest()[:32]
                masks[other_party] = mask
        return masks
    
    def apply_masks(self, gradients: List[float], party_id: int) -> List[float]:
        """Apply pairwise masks to gradients"""
        masks = self.generate_pairwise_masks(party_id)
        masked_gradients = gradients.copy()
        
        for other_party, mask in masks.items():
            # Simple XOR masking (in practice, use more sophisticated methods)
            for i, grad in enumerate(masked_gradients):
                masked_gradients[i] += int.from_bytes(mask[i % len(mask):i % len(mask) + 4], 'big') / 1e9
        
        return masked_gradients