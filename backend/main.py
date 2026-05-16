from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.ai.hybrid_mapper import apply_ai_hybrid
from backend.classifier.page_classifier import classify_page
from backend.mapper.field_mapper import map_fields
from backend.ai.vector_store import embed_and_store
from backend.mapper.semantic_extractor import semantic_extract_fields
from backend.ai.supervisor import supervise_payloads
from backend.mapper.html_inference import inferred_fields, load_schema, load_schema_document, build_payload_from_flat
from backend.parser.docx_reader import read_upload_file
from backend.parser.section_parser import group_sections
from backend.utils.env import load_env_file
from backend.validators.validator import validate_payload

load_env_file(Path(__file__).with_name(".env"), override=True)

app = FastAPI(title="DegreeBaba Parser", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/parse")
async def parse_docx(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    parsed_docx = await read_upload_file(file)
    sections = group_sections(parsed_docx)
    classification = classify_page(parsed_docx["raw_text"], sections)
    page_type = classification["page_type"]
    schema_document = load_schema_document(page_type)
    mapped_fields, mapping_metadata, flat_mapped_fields = map_fields(page_type, sections, parsed_docx["raw_text"])
    
    # Run Engine 1: Deterministic AI Hybrid
    engine1_mapped, engine1_flat, mapping_metadata, ai_warnings, ai_review = apply_ai_hybrid(
        page_type=page_type,
        raw_text=parsed_docx["raw_text"],
        sections=sections,
        schema_document=schema_document,
        flat_values=flat_mapped_fields,
        metadata=mapping_metadata,
    )
    
    # Embed Document for Engine 2
    collection_name = file.filename.replace(".docx", "").replace(" ", "_").lower()
    final_mapped_fields = engine1_mapped
    final_flat_fields = engine1_flat
    flat_schema_fields = load_schema(page_type)

    try:
        embed_and_store(collection_name, parsed_docx["raw_text"])
        
        # Run Engine 2: Semantic Extractor
        engine2_flat = semantic_extract_fields(collection_name, flat_schema_fields)
        
        # Run Engine 3: Supervisor
        final_flat_fields = supervise_payloads(engine1_flat, engine2_flat, flat_schema_fields)
        final_mapped_fields = build_payload_from_flat(schema_document, final_flat_fields)
    except Exception as e:
        ai_warnings.append(f"Engine 2/3 failed, falling back to Engine 1: {str(e)}")
    
    validation = validate_payload(flat_schema_fields, final_flat_fields, classification)
    validation["warnings"].extend(ai_warnings)

    needs_manual_review = (
        classification["needs_manual_review"]
        or bool(validation["missing_fields"])
        or bool(validation.get("unmapped_fields"))
        or not ai_review["configured"]
        or any("Ambiguous" in warning for warning in validation["warnings"])
        or any(warning.startswith("AI ") for warning in validation["warnings"])
    )

    return {
        "page_type": page_type,
        "classification_confidence": classification["confidence"],
        "classification_scores": classification["scores"],
        "inferred_fields": inferred_fields(page_type),
        "mapped_fields": final_mapped_fields,
        "mapping_metadata": mapping_metadata,
        "ai_review": ai_review,
        "validation": validation,
        "needs_manual_review": needs_manual_review,
    }
