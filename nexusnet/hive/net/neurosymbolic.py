"""Wave-6: neurosymbolic reasoning layer (neural prediction + a symbolic rule engine).

Canon C07M0227 (Neurosymbolic Reasoning Layer): combine neural pattern recognition with a symbolic
logic engine + knowledge so the model can apply hard constraints and entailments. Here a forward-
chaining rule engine derives facts, and `NeuroSymbolicReasoner` adjusts the neural logits:
  - HARD constraints forbid classes the symbolic state rules out (logit -> -inf), guaranteeing the
    output respects known constraints.
  - SOFT entailments boost classes the rules support (additive bias), still differentiable.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import torch


@dataclass
class Rule:
    """IF all `antecedents` are known facts THEN assert `consequent` (forward chaining)."""
    antecedents: tuple[str, ...]
    consequent: str


class SymbolicRuleEngine:
    """Forward-chaining engine over a fact set; computes the deductive closure."""

    def __init__(self, rules: list[Rule] | None = None) -> None:
        self.rules = list(rules or [])

    def add_rule(self, antecedents: tuple[str, ...], consequent: str) -> None:
        self.rules.append(Rule(tuple(antecedents), consequent))

    def infer(self, facts: set[str]) -> set[str]:
        known = set(facts)
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                if rule.consequent not in known and all(a in known for a in rule.antecedents):
                    known.add(rule.consequent)
                    changed = True
        return known


class NeuroSymbolicReasoner:
    """Adjust neural class logits with symbolic constraints (hard forbid) and entailments (soft boost)."""

    def __init__(
        self,
        num_classes: int,
        *,
        forbid_fn: Callable[[set[str]], set[int]] | None = None,
        entail_fn: Callable[[set[str]], set[int]] | None = None,
        boost: float = 3.0,
    ) -> None:
        self.num_classes = num_classes
        self.forbid_fn = forbid_fn
        self.entail_fn = entail_fn
        self.boost = boost

    def apply(self, logits: torch.Tensor, derived_facts: set[str]) -> torch.Tensor:
        out = logits.clone()
        if self.forbid_fn:
            for c in self.forbid_fn(derived_facts):
                if 0 <= c < self.num_classes:
                    out[..., c] = float("-inf")           # hard constraint: class ruled out
        if self.entail_fn:
            for c in self.entail_fn(derived_facts):
                if 0 <= c < self.num_classes:
                    out[..., c] = out[..., c] + self.boost  # soft entailment boost
        return out

    def reason(self, logits: torch.Tensor, facts: set[str], engine: SymbolicRuleEngine) -> torch.Tensor:
        """Run the rule engine to closure on `facts`, then constrain/boost the logits."""
        return self.apply(logits, engine.infer(facts))
