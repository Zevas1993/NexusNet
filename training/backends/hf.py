
import torch
from dataclasses import dataclass
from typing import List
from transformers import AutoTokenizer, AutoModelForCausalLM

@dataclass
class HFConfig:
    model_id: str
    device: str = "cpu"
    max_new_tokens: int = 128
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 50
    do_sample: bool = True

class HFBackend:
    def __init__(self, cfg: HFConfig):
        self.cfg = cfg
        self.tok = AutoTokenizer.from_pretrained(cfg.model_id)
        self.m = AutoModelForCausalLM.from_pretrained(cfg.model_id)
        self.m.to(cfg.device); self.m.eval()
        if self.tok.pad_token_id is None: self.tok.pad_token_id = self.tok.eos_token_id

    def generate(self, prompts: List[str]) -> List[str]:
        outs = []
        for p in prompts:
            x = self.tok(p, return_tensors="pt").to(self.cfg.device)
            with torch.no_grad():
                y = self.m.generate(**x, max_new_tokens=self.cfg.max_new_tokens,
                                    temperature=self.cfg.temperature, top_p=self.cfg.top_p,
                                    top_k=self.cfg.top_k, do_sample=self.cfg.do_sample,
                                    pad_token_id=self.tok.pad_token_id)
            outs.append(self.tok.decode(y[0], skip_special_tokens=True))
        return outs

    def logprobs(self, prompts: List[str], completions: List[str]) -> List[float]:
        logps = []
        for p, c in zip(prompts, completions):
            full = p + c
            xf = self.tok(full, return_tensors="pt").to(self.cfg.device)
            xp = self.tok(p, return_tensors="pt").to(self.cfg.device)
            with torch.no_grad():
                out = self.m(**xf, labels=xf["input_ids"])
                logits = out.logits[:, :-1, :]
                labels = xf["input_ids"][:, 1:]
                prompt_len = xp["input_ids"].shape[1]
                mask = torch.zeros_like(labels, dtype=torch.float32).to(self.cfg.device)
                mask[:, prompt_len-1:] = 1.0
                logsoft = logits.log_softmax(dim=-1)
                token_logp = logsoft.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
                logps.append((token_logp * mask).sum().item())
        return logps

    def sft_step(self, prompts: List[str], targets: List[str], lr: float = 5e-6):
        self.m.train(); opt = torch.optim.AdamW(self.m.parameters(), lr=lr)
        tot = 0.0
        for p, y in zip(prompts, targets):
            xy = self.tok(p + y, return_tensors="pt").to(self.cfg.device)
            out = self.m(**xy, labels=xy["input_ids"])
            tot += float(out.loss.detach().cpu().item())
            out.loss.backward()
        torch.nn.utils.clip_grad_norm_(self.m.parameters(), 1.0)
        opt.step(); opt.zero_grad(set_to_none=True); self.m.eval()
        return {"sft_loss": tot / max(1, len(prompts))}
