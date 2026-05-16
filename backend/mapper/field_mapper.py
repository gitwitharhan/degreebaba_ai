from __future__ import annotations

from backend.mapper.base_mapper import MappingBuilder
from backend.mapper.course_mapper import map_course
from backend.mapper.html_inference import load_schema, load_schema_document
from backend.mapper.specialization_mapper import map_specialization
from backend.mapper.university_mapper import map_university


PAGE_MAPPERS = {
    "university": map_university,
    "course": map_course,
    "specialization": map_specialization,
}


def map_fields(page_type: str, sections: list[dict], raw_text: str) -> tuple[dict, dict, dict]:
    schema_document = load_schema_document(page_type)
    schema_fields = load_schema(page_type)
    builder = MappingBuilder(schema_fields, schema_document)

    mapper = PAGE_MAPPERS.get(page_type)
    if mapper:
        mapper(builder, sections, raw_text)

    return builder.build_payload(), builder.metadata, builder.values
