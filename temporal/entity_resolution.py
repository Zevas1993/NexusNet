
from __future__ import annotations
import re

ALIASES = {
    "openai": {"oai","open ai"},
    "google": {"alphabet", "google llc"},
    "microsoft": {"msft","microsoft corp","microsoft corporation"},
}

def normalize(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'[^a-z0-9\s\-\._]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def canonicalize(entity: str) -> str:
    n = normalize(entity)
    for k,vs in ALIASES.items():
        if n == k or n in vs:
            return k
    return n

def resolve_entities(entities: List[str]) -> Dict[str, str]:
    """Resolve a list of entities to their canonical forms"""
    resolved = {}
    for entity in entities:
        resolved[entity] = canonicalize(entity)
    return resolved

def get_entity_variants(canonical: str) -> List[str]:
    """Get all known variants of a canonical entity"""
    for k, vs in ALIASES.items():
        if k == canonical:
            return [canonical] + list(vs)
    return [canonical]

def find_similar_entities(query: str, threshold: float = 0.8) -> List[Tuple[str, float]]:
    """Find entities similar to the query (basic implementation)"""
    # This would use fuzzy matching libraries like fuzzywuzzy in production
    similar = []
    q_norm = normalize(query)

    for canonical, variants in ALIASES.items():
        # Check canonical form
        if _similarity_score(q_norm, canonical) >= threshold:
            similar.append((canonical, _similarity_score(q_norm, canonical)))

        # Check variants
        for variant in variants:
            if _similarity_score(q_norm, variant) >= threshold:
                similar.append((canonical, _similarity_score(q_norm, variant)))

    return sorted(similar, key=lambda x: x[1], reverse=True)

def _similarity_score(s1: str, s2: str) -> float:
    """Simple string similarity score (0.0 to 1.0)"""
    # This is a basic implementation - production would use Levenshtein distance
    s1_words = set(s1.lower().split())
    s2_words = set(s2.lower().split())

    if not s1_words or not s2_words:
        return 0.0

    intersection = s1_words.intersection(s2_words)
    union = s1_words.union(s2_words)

    return len(intersection) / len(union) if union else 0.0

def validate_entity(entity: str) -> Dict[str, Any]:
    """Validate entity and return validation info"""
    normalized = normalize(entity)
    canonical = canonicalize(entity)

    return {
        "original": entity,
        "normalized": normalized,
        "canonical": canonical,
        "is_known": canonical in ALIASES or any(variant == normalized for variants in ALIASES.values() for variant in variants),
        "confidence": 1.0 if canonical in ALIASES else 0.5,
        "variants": get_entity_variants(canonical)
    }

def merge_entity_mentions(entities: List[str]) -> List[Tuple[str, List[str]]]:
    """Group entity mentions by their canonical form"""
    groups = {}

    for entity in entities:
        canonical = canonicalize(entity)
        if canonical not in groups:
            groups[canonical] = []
        groups[canonical].append(entity)

    return [(canonical, mentions) for canonical, mentions in groups.items()]

def update_entity_aliases(new_aliases: Dict[str, List[str]]) -> bool:
    """Update the entity aliases dictionary (thread-safe would be better)"""
    global ALIASES
    try:
        ALIASES.update(new_aliases)
        return True
    except Exception:
        return False

def get_entity_statistics() -> Dict[str, Any]:
    """Get statistics about known entities"""
    total_canonical_entities = len(ALIASES)
    total_variants = sum(len(variants) for variants in ALIASES.values())

    return {
        "canonical_entities": total_canonical_entities,
        "total_variants": total_variants,
        "entities": list(ALIASES.keys())
