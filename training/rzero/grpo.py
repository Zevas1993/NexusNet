
import torch
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class GRPOConfig:
    lr: float = 1e-6
    kl_coef: float = 0.02

class GRPOTrainer:
    def __init__(self, backend, cfg: GRPOConfig):
        self.backend = backend
        self.cfg = cfg
        self.opt = torch.optim.AdamW(self.backend.m.parameters(), lr=cfg.lr)

    def step(self, prompts: List[str], completions: List[str], rewards: List[float]) -> Dict:
        R = torch.tensor(rewards, dtype=torch.float32, device=self.backend.m.device if hasattr(self.backend.m, 'device') else 'cpu')
        adv = R - R.mean()
        logps = self.backend.logprobs(prompts, completions)
        logps_t = torch.tensor(logps, dtype=torch.float32, device=R.device)
        pg = -(adv.detach() * logps_t).mean()
        kl = (logps_t ** 2).mean()
        loss = pg + self.cfg.kl_coef * kl
        self.opt.zero_grad(set_to_none=True); loss.backward()
        torch.nn.utils.clip_grad_norm_(self.backend.m.parameters(), 1.0)
        self.opt.step()
        return {"loss": float(loss.detach().cpu().item()), "pg": float(pg.detach().cpu().item()), "kl": float(kl.detach().cpu().item()), "R": float(R.mean().item())}
