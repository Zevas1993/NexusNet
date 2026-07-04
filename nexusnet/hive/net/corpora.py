"""Wave-3: per-EXPERT domain corpora derived from each capsule's designed area of expertise.

Canon: "the curriculum will be based on the expert node's designed area of expertise." Each expert
trains on a corpus whose lexicon and structure come from its OWN domain (area_of_expertise +
task_families in `hive.curriculum`), so different experts learn genuinely different distributions.

These are deterministic, synthetic-but-domain-grounded corpora (a template grammar over the domain's
own vocabulary) suitable for offline/CPU training and tests. A production run swaps in real domain
datasets behind the same `domain_corpus_for_capsule` seam.
"""
from __future__ import annotations

import random
import re

from ..curriculum import EXPERT_CAPSULES, CAPSULE_KEYS

# scaffold so every domain has enough grammatical glue even if its AOE string is short
_SCAFFOLD_VERBS = ["models", "analyzes", "predicts", "derives", "evaluates", "refines", "maps"]
_SCAFFOLD_OBJS = ["pattern", "structure", "signal", "system", "result", "method", "state"]
_STOP = {"the", "and", "for", "with", "from", "into", "via", "per"}


def _domain_lexicon(text: str) -> list[str]:
    words = [w for w in re.findall(r"[a-zA-Z]+", text.lower()) if len(w) > 2 and w not in _STOP]
    # de-dup preserving order
    seen: dict[str, None] = {}
    for w in words:
        seen.setdefault(w, None)
    return list(seen.keys())


def build_domain_corpus(
    area_of_expertise: str,
    task_families: list[str] | None = None,
    *,
    n_sentences: int = 400,
    seed: int = 0,
) -> str:
    """A template grammar ('the <subj> <verb> the <obj> . ') over the DOMAIN's own vocabulary.

    Held-out sentences are new combinations of known domain words, so a model that learns the domain
    structure (not memorizes) generalizes. Distinct domains -> distinct lexicons -> distinct corpora.
    """
    lex = _domain_lexicon(f"{area_of_expertise} {' '.join(task_families or [])}")
    if len(lex) < 4:
        lex = (lex + _SCAFFOLD_OBJS)
    subjects = lex
    verbs = (lex[:: 2] or _SCAFFOLD_VERBS) + _SCAFFOLD_VERBS
    objects = lex + _SCAFFOLD_OBJS
    rng = random.Random(seed)
    parts = [
        f"the {rng.choice(subjects)} {rng.choice(verbs)} the {rng.choice(objects)} . "
        for _ in range(n_sentences)
    ]
    return "".join(parts)


_RELATIONS = ["depends on", "contrasts with", "generalizes", "constrains", "derives from", "informs"]
_HYPERNYMS = ["concept", "method", "structure", "process", "principle", "system"]


def build_rich_domain_corpus(
    area_of_expertise: str,
    task_families: list[str] | None = None,
    *,
    n_sentences: int = 400,
    seed: int = 0,
) -> str:
    """A richer, multi-FORM domain grammar (definitional / relational / procedural / causal) over the
    domain's own vocabulary. Unlike the flat template, this forces the LM to learn several sentence
    structures + term relationships, so loss reduction reflects genuine structure learning, not a
    single memorized pattern. Deterministic; held-out sentences are novel term combinations.
    """
    lex = _domain_lexicon(f"{area_of_expertise} {' '.join(task_families or [])}")
    if len(lex) < 6:
        lex = lex + _SCAFFOLD_OBJS + _SCAFFOLD_VERBS
    rng = random.Random(seed)
    terms = lex
    verbs = (lex[::3] or _SCAFFOLD_VERBS) + _SCAFFOLD_VERBS
    parts: list[str] = []
    for _ in range(n_sentences):
        form = rng.randint(0, 3)
        t1, t2 = rng.choice(terms), rng.choice(terms)
        if form == 0:    # definitional
            parts.append(f"a {t1} is a {rng.choice(_HYPERNYMS)} that {rng.choice(verbs)} {rng.choice(terms)} . ")
        elif form == 1:  # relational
            parts.append(f"the {t1} {rng.choice(_RELATIONS)} the {t2} . ")
        elif form == 2:  # procedural
            parts.append(f"to {rng.choice(verbs)} the {t1} , first {rng.choice(verbs)} the {t2} then {rng.choice(verbs)} the {rng.choice(terms)} . ")
        else:            # causal
            parts.append(f"when the {t1} {rng.choice(verbs)} , the {t2} {rng.choice(verbs)} the {rng.choice(terms)} . ")
    return "".join(parts)


def domain_corpus_for_capsule(capsule_key: str, *, n_sentences: int = 400, seed: int = 0,
                              rich: bool = False) -> str:
    """Build the domain corpus for a named curriculum capsule (e.g. 'vision', 'physicist')."""
    if capsule_key not in EXPERT_CAPSULES:
        raise KeyError(f"unknown capsule {capsule_key!r}")
    cap = EXPERT_CAPSULES[capsule_key]
    builder = build_rich_domain_corpus if rich else build_domain_corpus
    return builder(
        cap["area_of_expertise"], cap.get("task_families"), n_sentences=n_sentences, seed=seed
    )


def all_domain_corpora(*, n_sentences: int = 200, seed: int = 0) -> dict[str, str]:
    """One domain corpus per expert capsule (keyed by capsule key)."""
    return {k: domain_corpus_for_capsule(k, n_sentences=n_sentences, seed=seed) for k in CAPSULE_KEYS}
