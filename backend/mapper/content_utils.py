from __future__ import annotations

import re
from typing import Iterable

from backend.mapper.fuzzy_mapper import best_section, similarity, slug
from backend.parser.table_parser import table_to_repeater


def first_non_empty_line(text: str) -> str | None:
    return next((line.strip() for line in text.splitlines() if line.strip()), None)


def html_from_text(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    return "".join(f"<p>{escape_html(line)}</p>" for line in lines)


def html_or_text(section: dict | None) -> str | None:
    if not section:
        return None
    return section["html"] or html_from_text(section["text"])


def lines(text: str) -> list[str]:
    return [re.sub(r"^(\d+[).]|-|\*)\s*", "", line.strip()) for line in text.splitlines() if line.strip()]


def split_title_description(line: str) -> tuple[str, str | None]:
    parts = re.split(r"[:-]", line, maxsplit=1)
    title = parts[0].strip()
    description = parts[1].strip() if len(parts) > 1 else None
    return title, description


def extract_stats(text: str, value_key: str = "value", label_key: str = "label", limit: int = 6) -> list[dict]:
    stats = []
    seen = set()
    for match in re.finditer(r"(\d+(?:\.\d+)?\s*(?:K|L|Cr|%|\+)?)", text, re.I):
        value = re.sub(r"\s+", "", match.group(1))[:6]
        context = text[max(0, match.start() - 45) : match.end() + 75].lower()
        label = "Stat"
        if "student" in context or "learner" in context:
            label = "Students"
        elif "alumni" in context:
            label = "Alumni"
        elif "faculty" in context:
            label = "Faculty"
        elif "partner" in context or "recruiter" in context or "hiring" in context:
            label = "Hiring Partners"
        elif "program" in context:
            label = "Programs"
        elif "salary" in context or "lpa" in context:
            label = "Salary"
        key = value
        if key in seen:
            continue
        seen.add(key)
        stats.append({value_key: value, label_key: label})
        if len(stats) >= limit:
            break
    return stats


def extract_faqs(text: str, answer_key: str = "answer") -> list[dict]:
    # Normalizing question lines by ensuring they are separate paragraphs if they contain a '?'
    text = re.sub(r"([?.!])\s+([A-Z][^.!?]*\?)", r"\1\n\2", text)
    source_lines = lines(text)
    faqs = []
    index = 0
    while index < len(source_lines):
        current = source_lines[index]
        # Check for trailing '?' or common FAQ patterns like "Q:" or "What is..."
        is_question = current.endswith("?") or re.match(r"^(q:|how|what|why|is|does|can)\s", current, re.I)
        if is_question:
            question = current
            index += 1
            answers = []
            while index < len(source_lines):
                next_line = source_lines[index]
                if next_line.endswith("?") or re.match(r"^(q:|how|what|why|is|does|can)\s", next_line, re.I):
                    break
                answers.append(next_line)
                index += 1
            faqs.append({"question": question, answer_key: html_from_text("\n".join(answers)) if answers else None})
        else:
            index += 1
    return faqs


def extract_steps(text: str) -> list[dict]:
    output = []
    for line in lines(text):
        match = re.match(r"step\s*(\d+)\.?\s*(.*)", line, re.I)
        if match:
            number = match.group(1)
            body = match.group(2).strip()
            title, description = split_title_description(body)
            output.append(
                {
                    "step_number": number,
                    "step_title": title,
                    "step_description": html_from_text(description or body),
                }
            )
    return output


def extract_simple_cards(text: str, title_key: str, description_key: str) -> list[dict]:
    cards = []
    for line in lines(text):
        title, description = split_title_description(line)
        cards.append({title_key: title, description_key: html_from_text(description or title)})
    return cards


def find_section(sections: list[dict], *keywords: str) -> dict | None:
    field = {"name": slug(" ".join(keywords) or "field"), "aliases": list(keywords)}
    match = best_section(field, sections, threshold=0.35)
    return match["section"] if match else None


def section_index(sections: list[dict], target: dict | None) -> int:
    if not target:
        return -1
    for index, section in enumerate(sections):
        if section is target:
            return index
    return -1


def between_sections(sections: list[dict], start_keywords: Iterable[str], stop_keywords: Iterable[str]) -> list[dict]:
    start = find_section(sections, *start_keywords)
    if not start:
        return []
    start_index = section_index(sections, start)
    stop_index = len(sections)
    for index in range(start_index + 1, len(sections)):
        heading = sections[index]["heading"].lower()
        if any(keyword.lower() in heading for keyword in stop_keywords):
            stop_index = index
            break
    return sections[start_index + 1 : stop_index]


def collect_heading_items(sections: list[dict], start_keywords: Iterable[str], stop_keywords: Iterable[str]) -> list[str]:
    output = []
    for section in between_sections(sections, start_keywords, stop_keywords):
        if section["heading"] and section["heading"] != "Document Start":
            output.append(section["heading"])
    return output


def all_tables(sections: list[dict]) -> list[list[list[str]]]:
    tables = []
    for section in sections:
        tables.extend(section.get("tables", []))
    return tables


def select_table(sections: list[dict], *header_keywords: str) -> list[list[str]] | None:
    best_match = None
    best_score = 0.0
    for table in all_tables(sections):
        if not table:
            continue
        header_text = " ".join(table[0]).lower()
        score = sum(1 for keyword in header_keywords if keyword.lower() in header_text)
        fuzzy = sum(similarity(keyword, header_text) for keyword in header_keywords)
        total = score + fuzzy
        if total > best_score:
            best_score = total
            best_match = table
    return best_match


def repeater_from_heading_items(
    items: list[str],
    field_name: str,
    extra_field_name: str | None = None,
    extra_value=None,
) -> list[dict]:
    rows = []
    for item in items:
        row = {field_name: item}
        if extra_field_name is not None:
            row[extra_field_name] = extra_value
        rows.append(row)
    return rows


def map_table(table: list[list[str]] | None, children: list[str]) -> list[dict]:
    if not table:
        return []
    return table_to_repeater(table, children)


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )
