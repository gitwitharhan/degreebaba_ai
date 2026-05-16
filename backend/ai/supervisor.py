from __future__ import annotations

import json
from backend.ai.groq_client import chat_json

SUPERVISOR_SYSTEM_PROMPT = """You are the final Supervisor AI in a DOCX -> ACF mapping pipeline.
Your job is to compare the outputs of two extraction engines and select the absolute best value for each field.

Engine 1: Deterministic Mapper (Regex + Structural Rules). High accuracy for stats and tables.
Engine 2: Semantic AI (Embeddings + Context). High accuracy for paragraphs, descriptions, and UI marketing text.

Rules:
1. For every field, you will receive {"engine_1": value1, "engine_2": value2}.
2. If one is null and the other has a value, pick the one with a value.
3. If both have values, pick the one that is most accurate, detailed, and formatted best.
4. If BOTH are null but the field is a UI/Marketing field (like CTA text, form headings, button labels), you MUST synthesize a professional, context-aware value based on the rest of the document.
5. For tables/repeaters or strict stats, Engine 1 is usually better.
6. Return a JSON object with the exact field keys and the winning value. Do not nest them.
"""

def supervise_payloads(deterministic_flat: dict, semantic_flat: dict, flat_fields: list[dict]) -> dict:
    """Uses Groq to supervise and merge the two payloads field by field."""
    
    sections = {}
    for field in flat_fields:
        path_parts = field["name"].split('.')
        section_name = path_parts[0] if len(path_parts) > 1 else "general"
        if section_name not in sections:
            sections[section_name] = []
        sections[section_name].append(field["name"])

    final_payload = {}
    
    for section_name, field_names in sections.items():
        comparison_dict = {}
        has_conflict = False
        
        for name in field_names:
            val1 = deterministic_flat.get(name)
            val2 = semantic_flat.get(name)
            
            # Simple auto-resolve if one is completely empty
            if not val1 and not val2:
                # Still add to comparison_dict so Supervisor can synthesize if it's a UI field
                comparison_dict[name] = {
                    "engine_1": None,
                    "engine_2": None
                }
                has_conflict = True
            elif val1 and not val2:
                final_payload[name] = val1
            elif val2 and not val1:
                final_payload[name] = val2
            elif val1 == val2:
                final_payload[name] = val1
            else:
                # Both have values and they differ!
                comparison_dict[name] = {
                    "engine_1": val1,
                    "engine_2": val2
                }
                has_conflict = True
                
        if has_conflict:
            user_prompt = f"""
Section: {section_name}

Conflicting or Null Fields:
{json.dumps(comparison_dict, indent=2)}

Return a flat JSON object where keys are the field names, and values are the chosen winning values (or synthesized values for UI fields).
"""
            result, error = chat_json(system_prompt=SUPERVISOR_SYSTEM_PROMPT, user_prompt=user_prompt)
            
            if not error and isinstance(result, dict):
                for k, v in result.items():
                    final_payload[k] = v
            else:
                # Fallback to deterministic if AI fails
                for k, v in comparison_dict.items():
                    if k not in final_payload:
                        final_payload[k] = v["engine_1"]

    return final_payload
