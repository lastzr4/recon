"""Auto and manual field (column) mapping between two datasets."""
from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List, Optional, Tuple

FUZZY_MATCH_THRESHOLD = 0.82


@dataclass
class FieldMapping:
    """A single mapped field pair between File 1 and File 2."""

    field_1: str
    field_2: str
    match_type: str  # "exact" | "fuzzy" | "manual"
    is_primary_key: bool = False
    confidence: float = 1.0


def normalize_column_name(name: str) -> str:
    """Normalize a column name for case-insensitive, whitespace-trimmed comparison."""
    return " ".join(str(name).strip().lower().split())


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def auto_map_columns(
    columns_1: List[str], columns_2: List[str]
) -> Tuple[List[FieldMapping], List[str], List[str]]:
    """Automatically map columns between two column lists.

    Returns (mappings, unmapped_in_1, unmapped_in_2).

    Strategy:
      1. Exact match on normalized (lowercased, trimmed) names.
      2. For anything left over, fuzzy match using difflib similarity ratio
         against normalized names, subject to FUZZY_MATCH_THRESHOLD, greedily
         taking the best available pair each round.
    """
    remaining_1 = list(columns_1)
    remaining_2 = list(columns_2)
    norm_1 = {c: normalize_column_name(c) for c in columns_1}
    norm_2 = {c: normalize_column_name(c) for c in columns_2}

    mappings: List[FieldMapping] = []

    # Pass 1: exact normalized match
    for c1 in list(remaining_1):
        for c2 in list(remaining_2):
            if norm_1[c1] == norm_2[c2]:
                mappings.append(FieldMapping(field_1=c1, field_2=c2, match_type="exact", confidence=1.0))
                remaining_1.remove(c1)
                remaining_2.remove(c2)
                break

    # Pass 2: fuzzy match, greedy best-first
    while remaining_1 and remaining_2:
        best_score = 0.0
        best_pair: Optional[Tuple[str, str]] = None
        for c1 in remaining_1:
            for c2 in remaining_2:
                score = _similarity(norm_1[c1], norm_2[c2])
                if score > best_score:
                    best_score = score
                    best_pair = (c1, c2)
        if best_pair and best_score >= FUZZY_MATCH_THRESHOLD:
            c1, c2 = best_pair
            mappings.append(
                FieldMapping(field_1=c1, field_2=c2, match_type="fuzzy", confidence=round(best_score, 2))
            )
            remaining_1.remove(c1)
            remaining_2.remove(c2)
        else:
            break

    return mappings, remaining_1, remaining_2


def unmapped_fields(
    columns_1: List[str], columns_2: List[str], mappings: List[FieldMapping]
) -> Tuple[List[str], List[str]]:
    """Compute which columns from each file are not part of any mapping."""
    mapped_1 = {m.field_1 for m in mappings}
    mapped_2 = {m.field_2 for m in mappings}
    only_1 = [c for c in columns_1 if c not in mapped_1]
    only_2 = [c for c in columns_2 if c not in mapped_2]
    return only_1, only_2
