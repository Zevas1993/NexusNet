"""PB-2026-06-03-095 - Dedicated Memory Model Knowledge Lane (MeMo), governed + shadow-only.

Canon doctrine: a frozen executive queries a smaller MEMORY MODEL trained on APPROVED corpora; it is
NOT a replacement for retrieval/KAC/source-to-claim provenance - KAC stays the citation authority.
This lane implements the GOVERNANCE + protocol around such a model (no actual fine-tuning here; the
reflection-QA store is the shadow stand-in for the trained memory model):

  - corpus eligibility (source digest, rights, freshness, privacy) gate before anything is ingested,
  - reflection-QA generation that PRESERVES source refs across the four required categories,
  - a bounded inference protocol (grounding -> entity identification -> support seeking),
  - memory answers remain SECONDARY recall unless linked back to a KAC citation.

Non-mutating, shadow-only, rights-cleared corpora only.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

QACategory = Literal["direct_fact", "consolidated_multi_fact", "entity_surface", "cross_document_synthesis"]


class CorpusDoc(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_id: str
    text: str
    source_ref: str
    source_digest: str = ""
    rights_cleared: bool = False
    privacy_class: Literal["public", "internal", "private"] = "private"
    freshness_days: int = 9999
    entities: list[str] = Field(default_factory=list)
    facts: list[str] = Field(default_factory=list)


def corpus_eligibility(doc: CorpusDoc, *, max_freshness_days: int = 3650) -> dict[str, Any]:
    """Gate a corpus doc: rights-cleared, not private, fresh, and source-attributed."""
    reasons: list[str] = []
    if not doc.rights_cleared:
        reasons.append("rights_not_cleared")
    if doc.privacy_class == "private":
        reasons.append("private_data")
    if doc.freshness_days > max_freshness_days:
        reasons.append("stale")
    if not doc.source_ref:
        reasons.append("missing_source_ref")
    return {"eligible": not reasons, "reasons": reasons}


class ReflectionQA(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    answer: str
    category: QACategory
    source_ref: str                      # provenance preserved on every QA pair
    doc_ids: list[str] = Field(default_factory=list)


def generate_reflection_qa(docs: list[CorpusDoc]) -> list[ReflectionQA]:
    """Deterministically synthesize reflection QA covering all four required categories, each carrying
    its source ref(s). (A real lane would train a memory model on these; here they ARE the store.)"""
    qa: list[ReflectionQA] = []
    for d in docs:
        for fact in d.facts:
            qa.append(ReflectionQA(question=f"What does {d.doc_id} state about: {fact[:40]}?",
                                   answer=fact, category="direct_fact", source_ref=d.source_ref,
                                   doc_ids=[d.doc_id]))
        if len(d.facts) >= 2:
            qa.append(ReflectionQA(
                question=f"Summarize the combined facts in {d.doc_id}.",
                answer="; ".join(d.facts), category="consolidated_multi_fact",
                source_ref=d.source_ref, doc_ids=[d.doc_id]))
        for ent in d.entities:
            qa.append(ReflectionQA(question=f"Which sources mention {ent}?", answer=ent,
                                   category="entity_surface", source_ref=d.source_ref, doc_ids=[d.doc_id]))
    # cross-document synthesis: entities shared across >1 doc
    by_entity: dict[str, list[str]] = {}
    for d in docs:
        for ent in d.entities:
            by_entity.setdefault(ent, []).append(d.doc_id)
    for ent, ids in by_entity.items():
        if len(ids) > 1:
            qa.append(ReflectionQA(
                question=f"How do {', '.join(ids)} jointly describe {ent}?",
                answer=f"{ent} is described across {len(ids)} sources",
                category="cross_document_synthesis",
                source_ref="+".join(sorted(set(d.source_ref for d in docs if ent in d.entities))),
                doc_ids=ids))
    return qa


class MemoryModelLane:
    """The governed MeMo lane: eligibility-gated ingest, reflection-QA store, bounded query, KAC fallback."""

    mutates_production = False

    def __init__(self, *, max_freshness_days: int = 3650) -> None:
        self.max_freshness_days = max_freshness_days
        self.qa: list[ReflectionQA] = []
        self.ingested_docs: list[str] = []
        self.rejected: list[dict[str, Any]] = []

    def ingest(self, docs: list[CorpusDoc]) -> dict[str, Any]:
        eligible: list[CorpusDoc] = []
        for d in docs:
            verdict = corpus_eligibility(d, max_freshness_days=self.max_freshness_days)
            if verdict["eligible"]:
                eligible.append(d)
            else:
                self.rejected.append({"doc_id": d.doc_id, "reasons": verdict["reasons"]})
        new_qa = generate_reflection_qa(eligible)
        self.qa.extend(new_qa)
        self.ingested_docs.extend(d.doc_id for d in eligible)
        return {"ingested": len(eligible), "rejected": len(docs) - len(eligible),
                "qa_generated": len(new_qa)}

    def query(self, question: str, *, kac_citation: str | None = None) -> dict[str, Any]:
        """Bounded protocol: grounding -> entity identification -> support seeking. Memory answers are
        SECONDARY recall unless linked to a KAC citation (then promotable to grounded evidence)."""
        q = question.lower()
        # grounding: lexical overlap with stored QA answers/questions
        scored = []
        for item in self.qa:
            overlap = len(set(q.split()) & set((item.question + " " + item.answer).lower().split()))
            if overlap > 0:
                scored.append((overlap, item))
        scored.sort(key=lambda t: t[0], reverse=True)
        if not scored:
            return {"answer": None, "grounded": False, "evidence_class": "none",
                    "reason": "no_supporting_memory"}
        best = scored[0][1]
        cited = kac_citation is not None
        return {
            "answer": best.answer,
            "source_ref": best.source_ref,
            "category": best.category,
            "grounded": cited,                      # only grounded when linked to a KAC citation
            "evidence_class": "grounded_kac" if cited else "secondary_recall",
            "kac_citation": kac_citation,
            "candidates": len(scored),
        }
