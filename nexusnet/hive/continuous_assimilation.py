"""Continuous Ivy-League assimilation - the wrapper's learning engine (canon C39M0238).

The canon end-to-end deliverable is a WRAPPER people use: it wraps local + API models, and DURING
usage it learns from the wrapped models - pulls/assimilates their knowledge/capabilities, packages it
into the CORRECT expert node, and TAGS it with provenance (the source model). Once a node has
assimilated enough source models it TRAINS. Ivy-League training is therefore CONSTANT/continuous, not
one-time; the replace/alert threshold for an expert is the current top-rated model in that domain.

This is that loop: assimilate-during-usage -> route to expert node -> provenance-tag -> threshold ->
train -> keep assimilating. It is what turns ordinary wrapper usage (over many users, over time) into
growth of the born model. Deterministic, non-mutating; training is a SIGNAL the trainer acts on.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AssimilationRecord:
    """One provenance-tagged knowledge capture from a wrapped model, routed to an expert node."""
    source_model: str
    expert_node: str
    task: str = ""
    quality: float = 1.0
    knowledge_ref: str = ""              # a ref/summary of the captured knowledge (never raw private data)
    metadata: dict[str, Any] = field(default_factory=dict)


class ContinuousAssimilationLoop:
    """Assimilate wrapped-model knowledge into expert nodes during usage; signal training at threshold."""

    mutates_production = False

    def __init__(self, *, train_threshold: int = 3) -> None:
        self.train_threshold = train_threshold
        self._banks: dict[str, list[AssimilationRecord]] = {}   # expert_node -> capture records
        self._trained_rounds: dict[str, int] = {}               # expert_node -> times trained

    def assimilate(self, *, source_model: str, expert_node: str, task: str = "",
                   quality: float = 1.0, knowledge_ref: str = "",
                   metadata: dict[str, Any] | None = None) -> AssimilationRecord:
        """Capture a wrapped model's knowledge into an expert node, provenance-tagged by source model."""
        rec = AssimilationRecord(source_model=source_model, expert_node=expert_node, task=task,
                                 quality=quality, knowledge_ref=knowledge_ref,
                                 metadata=dict(metadata or {}))
        self._banks.setdefault(expert_node, []).append(rec)
        return rec

    def source_models(self, expert_node: str) -> list[str]:
        """The DISTINCT source models assimilated into a node (the provenance set)."""
        return sorted({r.source_model for r in self._banks.get(expert_node, [])})

    def assimilation_count(self, expert_node: str) -> int:
        """How many distinct source models have been assimilated into this node."""
        return len(self.source_models(expert_node))

    def captures(self, expert_node: str) -> int:
        return len(self._banks.get(expert_node, []))

    def ready_to_train(self, expert_node: str) -> bool:
        """A node is training-ready once it has assimilated >= threshold distinct source models."""
        return self.assimilation_count(expert_node) >= self.train_threshold

    # --- take the BEST outputs over time to train (curate quality, not just quantity) ---

    def best_outputs(self, expert_node: str, *, top_k: int = 5) -> list[AssimilationRecord]:
        """The highest-quality captures for a node - the wrapper trains on the BEST, not all."""
        recs = sorted(self._banks.get(expert_node, []), key=lambda r: r.quality, reverse=True)
        return recs[:top_k]

    def curated_training_set(self, expert_node: str, *, top_k: int = 5,
                             min_quality: float = 0.0) -> list[dict[str, Any]]:
        """The curated best-output training set for an expert (quality-filtered + ranked)."""
        return [{"source_model": r.source_model, "knowledge_ref": r.knowledge_ref,
                 "quality": r.quality, "task": r.task}
                for r in self.best_outputs(expert_node, top_k=top_k) if r.quality >= min_quality]

    def best_source_for(self, expert_node: str) -> str | None:
        """The source model whose assimilated outputs are highest-quality for this node."""
        best = self.best_outputs(expert_node, top_k=1)
        return best[0].source_model if best else None

    def training_ready_nodes(self) -> list[str]:
        """All expert nodes that have crossed the assimilation threshold this moment."""
        return sorted(n for n in self._banks if self.ready_to_train(n))

    def mark_trained(self, expert_node: str) -> dict[str, Any]:
        """Record that the trainer consumed this node's bank (continuous: assimilation keeps going)."""
        self._trained_rounds[expert_node] = self._trained_rounds.get(expert_node, 0) + 1
        consumed = self._banks.get(expert_node, [])
        sources = self.source_models(expert_node)
        self._banks[expert_node] = []                            # bank consumed; future captures re-fill
        return {"expert_node": expert_node, "round": self._trained_rounds[expert_node],
                "consumed_captures": len(consumed), "assimilated_sources": sources}

    def replace_target(self, expert_node: str, leaderboard: dict[str, str]) -> dict[str, Any]:
        """The replace/alert bar = the current top-rated model for the node's domain (per leaderboard)."""
        top = leaderboard.get(expert_node)
        assimilated = self.source_models(expert_node)
        return {"expert_node": expert_node, "replace_target_model": top,
                "already_assimilated": top in assimilated if top else False,
                "assimilated_sources": assimilated}

    def provenance(self, expert_node: str) -> list[dict[str, Any]]:
        """Per-source provenance for a node (source model + how many captures + mean quality)."""
        out: dict[str, dict[str, Any]] = {}
        for r in self._banks.get(expert_node, []):
            p = out.setdefault(r.source_model, {"source_model": r.source_model, "captures": 0, "q_sum": 0.0})
            p["captures"] += 1
            p["q_sum"] += r.quality
        return [{"source_model": p["source_model"], "captures": p["captures"],
                 "mean_quality": round(p["q_sum"] / p["captures"], 4)} for p in out.values()]

    def status(self) -> dict[str, Any]:
        nodes = sorted(self._banks)
        return {
            "train_threshold": self.train_threshold,
            "nodes": {n: {"distinct_sources": self.assimilation_count(n),
                          "captures": self.captures(n),
                          "ready_to_train": self.ready_to_train(n),
                          "trained_rounds": self._trained_rounds.get(n, 0)} for n in nodes},
            "training_ready_nodes": self.training_ready_nodes(),
            "continuous": True,                                  # training is recurring, not one-time
            "mutates_production": False,
        }
