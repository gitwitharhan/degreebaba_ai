from __future__ import annotations

import json

from backend.ai.groq_client import chat_json, groq_status, load_groq_config
from backend.mapper.html_inference import build_payload_from_flat


REVIEW_SYSTEM_PROMPT = """You are the AI review stage in a DOCX -> ACF mapping pipeline.

You are not the primary mapper. Deterministic extraction has already happened.
Your job is to:
- resolve ambiguous scalar fields
- improve missing hero stats
- stay faithful to source material

Hard rules:
- Never invent facts, fees, rankings, counts, banks, companies, accreditations, or names.
- If evidence is weak or absent, return null (except for generic UI text).
- For missing UI text (like CTAs, button text, form headings), you may generate sensible default marketing copy.
- WYSIWYG values must be valid HTML paragraphs.
- Do not rewrite already strong deterministic values unless the source text clearly supports a better value.
- Only return values for the requested fields.
"""

VERIFY_SYSTEM_PROMPT = """You are the AI verification stage in a DOCX -> ACF mapping pipeline.

You will receive proposed AI updates for a small set of fields.
Your job is to verify each proposed field strictly against the source sections and raw text.

Hard rules:
- If a proposed value is a fact/stat that is not directly supported by the source, reject it.
- Never invent replacement values for facts.
- For UI/Marketing fields (paths containing 'cta', 'button', 'heading', 'tag', 'text', 'title', etc.), ALWAYS approve sensible generated marketing copy. Do NOT reject them for missing from source.
- Approve fact values only if clearly grounded in the document.
- Return only JSON.
"""


def apply_ai_hybrid(
    *,
    page_type: str,
    raw_text: str,
    sections: list[dict],
    schema_document: dict,
    flat_values: dict,
    metadata: dict,
) -> tuple[dict, dict, dict, list[str], dict]:
    ready, status_message = groq_status()
    review_info = {
        "enabled": True,
        "configured": ready,
        "model": load_groq_config().model,
        "status": status_message,
        "reviewed_fields": [],
        "verified_fields": [],
    }

    candidate_fields = _candidate_fields(metadata)
    stat_field = _hero_stat_field(page_type, flat_values)
    if not candidate_fields and not stat_field:
        review_info["status"] = "No ambiguous fields needed AI review"
        return build_payload_from_flat(schema_document, flat_values), flat_values, metadata, [], review_info

    if not ready:
        warnings = ["AI review required but unavailable: " + status_message]
        return build_payload_from_flat(schema_document, flat_values), flat_values, metadata, warnings, review_info

    section_digest = "\n\n".join(
        f"[{index + 1}] {section['heading']}\n{section['text'][:600]}"
        for index, section in enumerate(sections[:10])
    )
    current_subset = _current_subset(flat_values, candidate_fields, stat_field)

    review_prompt = f"""
Page type: {page_type}
Requested scalar candidate fields: {candidate_fields}
Requested stat field: {stat_field}

Current values:
{_json_dump(current_subset)}

Sections:
{section_digest}

Raw text:
{raw_text[:3000]}

Return strict JSON with this shape:
{{
  "field_updates": {{
    "field.path": "value or <p>html</p> or null"
  }},
  "stat_update": {{
    "field": "field.path or null",
    "items": [{{}}]
  }}
}}
"""
    review_result, review_error = chat_json(system_prompt=REVIEW_SYSTEM_PROMPT, user_prompt=review_prompt)
    warnings: list[str] = []
    if review_error:
        warnings.append("AI review failed: " + review_error)
        review_info["status"] = review_error
        return build_payload_from_flat(schema_document, flat_values), flat_values, metadata, warnings, review_info
    if not review_result:
        warnings.append("AI review returned no result")
        review_info["status"] = "AI review returned no result"
        return build_payload_from_flat(schema_document, flat_values), flat_values, metadata, warnings, review_info

    proposed_updates = _collect_proposed_updates(review_result, candidate_fields, stat_field)
    review_info["reviewed_fields"] = sorted(proposed_updates.keys())
    if not proposed_updates:
        review_info["status"] = "AI review found no grounded updates"
        return build_payload_from_flat(schema_document, flat_values), flat_values, metadata, warnings, review_info

    verify_prompt = f"""
Page type: {page_type}

Proposed updates:
{_json_dump(proposed_updates)}

Sections:
{section_digest}

Return strict JSON:
{{
  "approved_fields": ["field.path"],
  "rejected_fields": {{
    "field.path": "short reason"
  }}
}}
"""
    verify_result, verify_error = chat_json(system_prompt=VERIFY_SYSTEM_PROMPT, user_prompt=verify_prompt)
    if verify_error:
        warnings.append("AI verification failed: " + verify_error)
        review_info["status"] = verify_error
        return build_payload_from_flat(schema_document, flat_values), flat_values, metadata, warnings, review_info

    approved_fields = set((verify_result or {}).get("approved_fields") or [])
    rejected_fields = (verify_result or {}).get("rejected_fields") or {}
    review_info["verified_fields"] = sorted(approved_fields)

    for path, reason in rejected_fields.items():
        warnings.append(f"AI rejected update for {path}: {reason}")

    for path, value in proposed_updates.items():
        if path not in approved_fields:
            continue
        flat_values[path] = value
        if path in metadata:
            metadata[path] = {
                **metadata[path],
                "mapped": _has_value(value),
                "resolver": f"ai:{load_groq_config().model}",
                "score": max(0.82, metadata[path].get("score", 0.0)),
            }

    if approved_fields:
        review_info["status"] = f"AI review applied {len(approved_fields)} verified updates"
    else:
        review_info["status"] = "AI review completed but no updates passed verification"

    return build_payload_from_flat(schema_document, flat_values), flat_values, metadata, warnings, review_info


def _candidate_fields(metadata: dict) -> list[str]:
    output = []
    for path, meta in metadata.items():
        field_type = meta.get("type")
        if field_type not in {"text", "textarea", "wysiwyg"}:
            continue
        if meta.get("mapped") and meta.get("score", 0) >= 0.72:
            continue
        if any(token in path for token in ("canonical_url", "slug", "logo", "image")):
            continue
        output.append(path)
    return output[:30]


def _hero_stat_field(page_type: str, flat_values: dict) -> str | None:
    candidates = {
        "university": "hero_section.hero_stats",
        "course": "hero_section.hero_stats",
        "specialization": "hero_section.hero_stats",
    }
    path = candidates.get(page_type)
    if not path:
        return None
    current = flat_values.get(path)
    if isinstance(current, list) and current:
        return None
    return path


def _collect_proposed_updates(review_result: dict, candidate_fields: list[str], stat_field: str | None) -> dict:
    updates: dict = {}
    for path, value in (review_result.get("field_updates") or {}).items():
        if path not in candidate_fields:
            continue
        if _has_value(value):
            updates[path] = value

    stat_update = review_result.get("stat_update") or {}
    if stat_field and stat_update.get("field") == stat_field and isinstance(stat_update.get("items"), list) and stat_update["items"]:
        updates[stat_field] = stat_update["items"]
    return updates


def _current_subset(flat_values: dict, candidate_fields: list[str], stat_field: str | None) -> dict:
    keys = list(candidate_fields)
    if stat_field:
        keys.append(stat_field)
    return {key: flat_values.get(key) for key in keys}


def _json_dump(value) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def _has_value(value) -> bool:
    if isinstance(value, list):
        return len(value) > 0
    return value is not None and str(value).strip() != ""
