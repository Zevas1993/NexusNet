
from dataclasses import dataclass
from typing import Tuple, List
@dataclass
class RZeroConfig:
    n_candidates: int = 128
    k_samples: int = 6
    informative_band: Tuple[int, int] = (2, 4)
    max_len: int = 512
    grpo_lr: float = 1e-6
    grpo_kl_coef: float = 0.02
    repetition_bleu_threshold: float = 0.85
    repetition_penalty_strength: float = 0.2
    format_required_tags: List[str] = ("<question>", "</question>", "<answer>", "</answer>")
    out_dir: str = "data/rzero"
    experiment: str = "default"
