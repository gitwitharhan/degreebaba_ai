from __future__ import annotations


def validate_payload(schema: list[dict], mapped_fields: dict, classification: dict) -> dict:
    missing_fields = []
    unmapped_fields = []
    thin_content = []
    warnings = []

    for field in schema:
        value = mapped_fields.get(field["name"])
        if field.get("required") and not _has_value(value):
            missing_fields.append(field["name"])
        if not _has_value(value):
            unmapped_fields.append(field["name"])
        
        # New: Check inside repeaters for null attributes
        if field["type"] == "repeater" and isinstance(value, list) and len(value) > 0:
            null_attrs = set()
            for item in value:
                if isinstance(item, dict):
                    for k, v in item.items():
                        if not _has_value(v):
                            null_attrs.add(k)
            if null_attrs:
                warnings.append(f"Incomplete repeater '{field['name']}': Missing attributes {list(null_attrs)}")

        if field["type"] == "wysiwyg" and isinstance(value, str):
            word_count = len(value.replace("<p>", " ").replace("</p>", " ").split())
            if word_count < 20:
                thin_content.append(field["name"])

        if field["type"] == "repeater" and value is not None and not isinstance(value, list):
            warnings.append(f"{field['name']} must be an array")

    stat_values = []
    stat_paths = (
        "hero_section.hero_stats",
        "hero_section.hero_facts",
        "overview_section.overview_stats",
        "placement_section.placement_stats",
        "hero_stats",
        "hero_facts",
    )
    for key in stat_paths:
        for item in mapped_fields.get(key) or []:
            if not isinstance(item, dict):
                continue
            value = item.get("value") or item.get("stat_value") or item.get("stat_number") or item.get("fact_value")
            if value:
                stat_values.append(value)

    duplicates = sorted({value for value in stat_values if stat_values.count(value) > 1})
    if duplicates:
        warnings.append(f"Duplicate stat values detected: {', '.join(duplicates)}")

    for value in stat_values:
        if len(str(value)) > 6:
            warnings.append(f'Stat value "{value}" exceeds 6 characters')

    if classification["confidence"] < 0.80:
        warnings.append("Ambiguous page type classification below 0.80")

    return {
        "missing_fields": missing_fields,
        "unmapped_fields": unmapped_fields,
        "thin_content": thin_content,
        "warnings": warnings,
    }


def _has_value(value) -> bool:
    if isinstance(value, list):
        return len(value) > 0
    return value is not None and str(value).strip() != ""
