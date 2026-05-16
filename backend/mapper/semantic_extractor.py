from __future__ import annotations

import json
from backend.ai.groq_client import chat_json
from backend.ai.vector_store import query_vector_store

SEMANTIC_EXTRACTION_PROMPT = """You are a Semantic Extraction AI.
Your task is to extract specific JSON fields from the provided document chunks.

Rules:
1. Return strictly JSON matching the requested keys.
2. If a field's value cannot be found or reasonably inferred from the chunks, set it to null.
3. For marketing or UI fields (like button texts, form headings, CTAs), you may generate sensible default marketing copy based on the context.
4. Do not invent factual data (stats, fees, names).
"""

def semantic_extract_fields(collection_name: str, flat_fields: list[dict]) -> dict:
    """Extracts all fields grouped by section using ChromaDB context and Groq."""
    
    # Group fields by their top-level section (e.g. 'hero_section', 'about_section')
    sections = {}
    for field in flat_fields:
        # Ignore repeaters for simplicity in semantic extraction, or handle them specifically?
        # The user wants ACF fields matched. We will ask for all fields.
        path_parts = field["name"].split('.')
        section_name = path_parts[0] if len(path_parts) > 1 else "general"
        
        if section_name not in sections:
            sections[section_name] = []
        sections[section_name].append(field)

    semantic_payload = {}
    
    # Process each section
    for section_name, fields in sections.items():
        # Build a query for this section
        field_names = [f["name"] for f in fields]
        query = f"Information about {section_name.replace('_', ' ')}. Relevant to: " + ", ".join([f["leaf_name"] for f in fields])
        
        # Retrieve context from ChromaDB
        chunks = query_vector_store(collection_name, query, n_results=5)
        if not chunks:
            continue
            
        context_text = "\n\n---\n\n".join(chunks)
        
        user_prompt = f"""
Section: {section_name}
Requested Fields:
{json.dumps(field_names, indent=2)}

Source Text Context:
{context_text}

Return a JSON object where the keys are exactly the Requested Fields, and values are the extracted strings or null.
"""
        result, error = chat_json(system_prompt=SEMANTIC_EXTRACTION_PROMPT, user_prompt=user_prompt)
        
        if not error and isinstance(result, dict):
            # Merge into the semantic payload
            for k, v in result.items():
                if v is not None and str(v).strip() != "":
                    semantic_payload[k] = v
                    
    return semantic_payload
