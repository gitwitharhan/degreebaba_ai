from __future__ import annotations

import re
from difflib import SequenceMatcher

from backend.mapper.html_inference import infer_template_sections


SIGNALS = {
    "university": [
        "university",
        "accreditation",
        "ranking",
        "faculty",
        "alumni",
        "recruiter",
        "placement",
        "multiple programs",
        "admission",
        "established year",
    ],
    "course": [
        "course",
        "program",
        "duration",
        "semester",
        "syllabus",
        "curriculum",
        "eligibility",
        "course facts",
        "specializations offered",
        "sample certificate",
    ],
    "specialization": [
        "specialization",
        "marketing",
        "finance",
        "hr",
        "analytics",
        "data science",
        "salary",
        "career scope",
        "job opportunities",
        "specialization fee",
    ],
}


def classify_page(raw_text: str, sections: list[dict]) -> dict:
    headings = [section["heading"] for section in sections]
    heading_text = " ".join(headings)
    first_heading = headings[0].lower() if headings else ""
    haystack = f"{raw_text}\n{heading_text}".lower()
    raw_scores = {page_type: 0.0 for page_type in SIGNALS}

    for page_type, signals in SIGNALS.items():
        raw_scores[page_type] += sum(len(re.findall(re.escape(signal), haystack)) for signal in signals)
        raw_scores[page_type] += _template_alignment_score(headings, page_type)

    strong_type = _strong_title_type(first_heading)
    if strong_type:
        raw_scores[strong_type] += 120
        for page_type in raw_scores:
            if page_type != strong_type:
                raw_scores[page_type] = max(0.0, raw_scores[page_type] - 18)

    raw_scores["specialization"] += _pattern_bonus(
        haystack,
        [
            r"specialization fee",
            r"job opportunities",
            r"salary",
            r"placement partners?",
            r"\bmba\s+in\s+[a-z ]+",
        ],
        7,
    )
    raw_scores["course"] += _pattern_bonus(
        haystack,
        [
            r"course facts",
            r"specializations offered",
            r"sample certificate",
            r"eligibility criteria",
            r"syllabus",
        ],
        6,
    )
    raw_scores["university"] += _pattern_bonus(
        haystack,
        [
            r"established year",
            r"pros of",
            r"accreditations?",
            r"faculty members?",
            r"reviews",
        ],
        5,
    )

    if "university online" in first_heading and strong_type is None:
        raw_scores["university"] += 28

    sorted_scores = sorted(raw_scores.items(), key=lambda item: item[1], reverse=True)
    page_type, top_score = sorted_scores[0]
    second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0
    total = sum(raw_scores.values()) or 1.0
    normalized_scores = {key: round(value / total, 4) for key, value in raw_scores.items()}

    confidence = _confidence_from_scores(
        top_score=top_score,
        second_score=second_score,
        strong_type=strong_type,
        predicted_type=page_type,
        template_score=_template_alignment_score(headings, page_type),
    )

    return {
        "page_type": page_type,
        "confidence": confidence,
        "scores": normalized_scores,
        "needs_manual_review": confidence < 0.80,
    }


def _template_alignment_score(headings: list[str], page_type: str) -> float:
    template_headings = infer_template_sections(page_type)
    if not headings or not template_headings:
        return 0.0

    best_scores = []
    for heading in headings[:18]:
        best_scores.append(max((_similarity(heading, template) for template in template_headings), default=0.0))

    average = sum(best_scores) / max(1, len(best_scores))
    high_matches = sum(1 for score in best_scores if score >= 0.60)
    medium_matches = sum(1 for score in best_scores if score >= 0.45)
    return average * 35 + high_matches * 6 + medium_matches * 2


def _strong_title_type(first_heading: str) -> str | None:
    # Specialization: "MBA in Marketing", "BBA in Finance"
    if re.search(r"\b(mba|bba|mca|bca|msc|bsc)\s+in\s+[a-z][a-z\s&]+\b", first_heading):
        return "specialization"
    # Course: "Online MBA", "Distance BBA", "Master of Business Administration"
    if re.search(r"\b(online|distance|master|bachelor|executive)?\s*(mba|bba|bca|mca|b\.?com|m\.?com|m\.?sc|b\.?sc)\b", first_heading):
        return "course"
    # University: Just the university name or "University Online"
    if "university" in first_heading or "institute" in first_heading or "academy" in first_heading:
        return "university"
    return None


def _pattern_bonus(haystack: str, patterns: list[str], weight: int) -> float:
    matches = sum(1 for pattern in patterns if re.search(pattern, haystack))
    return matches * weight


def _confidence_from_scores(
    *,
    top_score: float,
    second_score: float,
    strong_type: str | None,
    predicted_type: str,
    template_score: float,
) -> float:
    margin = top_score - second_score
    ratio = top_score / max(1.0, top_score + second_score)

    confidence = 0.55 + min(0.18, margin / 100) + min(0.15, ratio * 0.15) + min(0.10, template_score / 200)
    if strong_type == predicted_type:
        confidence += 0.15
    if margin >= 40:
        confidence += 0.07
    elif margin >= 20:
        confidence += 0.04

    return round(min(0.98, confidence), 2)


def _similarity(left: str, right: str) -> float:
    left_slug = _slug(left)
    right_slug = _slug(right)
    if not left_slug or not right_slug:
        return 0.0

    left_words = set(left_slug.split("-"))
    right_words = set(right_slug.split("-"))
    overlap = len(left_words & right_words) / max(1, len(left_words | right_words))
    ratio = SequenceMatcher(None, left_slug, right_slug).ratio() * 0.7
    contains = 0.25 if left_slug in right_slug or right_slug in left_slug else 0.0
    return min(1.0, max(overlap, ratio) + contains)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
