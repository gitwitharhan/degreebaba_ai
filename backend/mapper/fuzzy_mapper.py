from __future__ import annotations

import re
from difflib import SequenceMatcher


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def similarity(left: str, right: str) -> float:
    left_slug = slug(left)
    right_slug = slug(right)
    if not left_slug or not right_slug:
        return 0.0

    left_words = set(left_slug.split("-"))
    right_words = set(right_slug.split("-"))
    overlap = len(left_words & right_words) / max(1, len(left_words | right_words))
    ratio = SequenceMatcher(None, left_slug, right_slug).ratio()
    contains = 0.25 if left_slug in right_slug or right_slug in left_slug else 0
    return min(1.0, max(overlap, ratio * 0.7) + contains)


def best_section(field: dict, sections: list[dict], threshold: float = 0.42) -> dict | None:
    candidates = [
        field.get("section"),
        field["name"].replace("_", " "),
        *field.get("aliases", []),
    ]
    best = None
    for section in sections:
        for candidate in filter(None, candidates):
            score = similarity(candidate, section["heading"])
            if best is None or score > best["score"]:
                best = {"score": score, "section": section}

    return best if best and best["score"] >= threshold else None
