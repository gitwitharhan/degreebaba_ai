from __future__ import annotations

import re


def group_sections(parsed_docx: dict) -> list[dict]:
    sections: list[dict] = []
    current = {"heading": "Document Start", "content": [], "tables": []}

    for paragraph in parsed_docx.get("paragraphs", []):
        text = paragraph["text"].strip()
        if _is_heading(paragraph):
            if current["content"] or current["heading"] != "Document Start":
                sections.append(_finalize(current))
            current = {"heading": text, "content": [], "tables": []}
        else:
            current["content"].append(text)

    if current["content"] or current["heading"] != "Document Start":
        sections.append(_finalize(current))

    if not sections and parsed_docx.get("raw_text"):
        sections.append(
            {
                "heading": "Document Start",
                "text": parsed_docx["raw_text"],
                "html": _paragraphs_to_html(parsed_docx["raw_text"].splitlines()),
                "tables": parsed_docx.get("tables", []),
            }
        )

    attach_tables_to_nearest_section(sections, parsed_docx.get("tables", []))
    return sections


def attach_tables_to_nearest_section(sections: list[dict], tables: list[list[list[str]]]) -> None:
    if not sections:
        return
    table_index = 0
    for section in sections:
        if _table_section(section["heading"]) and table_index < len(tables):
            section["tables"].append(tables[table_index])
            table_index += 1


def _finalize(section: dict) -> dict:
    return {
        "heading": section["heading"],
        "text": "\n".join(section["content"]).strip(),
        "html": _paragraphs_to_html(section["content"]),
        "tables": section["tables"],
    }


def _paragraphs_to_html(lines: list[str]) -> str:
    return "".join(f"<p>{_escape(line)}</p>" for line in lines if line.strip())


def _is_heading(paragraph: dict) -> bool:
    style = paragraph.get("style", "").lower()
    text = paragraph.get("text", "").strip()
    if style.startswith("heading"):
        return True
    if len(text) > 90 or text.endswith((".", ":")):
        return False
    return bool(re.match(r"^[A-Z0-9]", text)) and len(text.split()) <= 9


def _table_section(heading: str) -> bool:
    return bool(re.search(r"program|course|fee|syllabus|salary|job|faculty|specialization", heading, re.I))


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )
