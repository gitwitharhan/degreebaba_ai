from __future__ import annotations

import re

from backend.mapper.base_mapper import MappingBuilder
from backend.mapper.content_utils import (
    collect_heading_items,
    extract_faqs,
    extract_stats,
    extract_steps,
    find_section,
    first_non_empty_line,
    html_from_text,
    html_or_text,
    lines,
    select_table,
)


def map_university(builder: MappingBuilder, sections: list[dict], raw_text: str) -> None:
    hero = find_section(sections, "short description")
    about = find_section(sections, "about")
    detail = find_section(sections, "detail")
    facts = find_section(sections, "facts")
    pros = find_section(sections, "pros", "why choose")
    accreditations = find_section(sections, "accreditations")
    admission = find_section(sections, "admission process")
    emi = find_section(sections, "emi")
    exam = find_section(sections, "examination process")
    programs = find_section(sections, "courses", "programs")
    faculty = find_section(sections, "faculty members")
    placement = find_section(sections, "placement partners", "placement")
    reviews = find_section(sections, "reviews")
    faq = find_section(sections, "faq")

    page_title = sections[0]["heading"] if sections else None
    hero_title = first_non_empty_line(page_title or "")
    hero_stats = extract_stats(raw_text, value_key="stat_number", label_key="stat_label")

    builder.set("page_type", "university", page_title, 1.0)
    builder.set("hero_section.university_name", hero_title, page_title, 1.0)
    builder.set("hero_section.university_full_name", hero_title, page_title, 1.0)
    builder.set(
        "hero_section.university_type",
        "University" if hero_title and "university" in hero_title.lower() else None,
        page_title,
        0.95,
    )
    builder.set("hero_section.hero_description", html_or_text(hero or about), _source(hero or about))
    builder.set("hero_section.hero_stats", hero_stats, "raw_text", 0.95)
    builder.set("hero_section.hero_badges", _hero_badges(detail, accreditations), _source(detail or accreditations), 0.85)

    programs_table = select_table(sections, "courses", "program fee", "eligibility")
    builder.set("lead_form_section.program_options", _program_options(programs_table), _source(programs))
    builder.set("about_section.about_heading", about["heading"] if about else None, _source(about))
    builder.set("about_section.about_content", html_or_text(about), _source(about))
    builder.set("about_section.quick_facts", _quick_facts(sections), "Amity Online Detail", 0.9)

    builder.set("why_choose_section.why_choose_heading", pros["heading"] if pros else None, _source(pros))
    builder.set("why_choose_section.why_choose_content", html_or_text(pros), _source(pros))
    builder.set("why_choose_section.why_choose_points", _points(pros, "point_title", "point_description"), _source(pros), 0.9)

    builder.set("university_facts_section.facts_heading", facts["heading"] if facts else None, _source(facts))
    builder.set("university_facts_section.facts_points", _points(facts, "fact_title", "fact_description"), _source(facts), 0.9)

    builder.set(
        "accreditation_section.accreditation_heading",
        accreditations["heading"] if accreditations else None,
        _source(accreditations),
    )
    builder.set(
        "accreditation_section.accreditations",
        _accreditation_rows(accreditations["text"] if accreditations else raw_text),
        _source(accreditations),
        0.9,
    )

    builder.set("programs_section.programs_heading", programs["heading"] if programs else None, _source(programs))
    builder.set("programs_section.programs", _program_rows(programs_table), _source(programs), 0.95)

    builder.set("admission_section.admission_heading", admission["heading"] if admission else None, _source(admission))
    builder.set("admission_section.admission_steps", extract_steps(admission["text"]) if admission else [], _source(admission), 0.95)

    builder.set("emi_section.emi_heading", emi["heading"] if emi else None, _source(emi))
    builder.set("emi_section.emi_description", html_or_text(emi), _source(emi))
    builder.set("emi_section.emi_feature_card.feature_tag", "EMI" if emi else None, _source(emi), 0.8)
    builder.set("emi_section.emi_feature_card.feature_title", emi["heading"] if emi else None, _source(emi))
    builder.set("emi_section.emi_feature_card.feature_description", html_or_text(emi), _source(emi))
    builder.set("emi_section.emi_feature_card.interest_rate", _interest_rate(emi["text"] if emi else raw_text), _source(emi), 0.8)
    builder.set("emi_section.emi_feature_card.emi_tenures", _tenures(emi["text"] if emi else raw_text), _source(emi), 0.85)
    builder.set("emi_section.emi_feature_card.emi_features", _emi_features(emi), _source(emi), 0.8)
    builder.set("emi_section.partner_banks", _simple_rows(_partner_banks(sections), "bank_name"), "EMI heading cluster", 0.9)

    builder.set("exam_section.exam_heading", exam["heading"] if exam else None, _source(exam))
    builder.set("exam_section.exam_description", html_or_text(exam), _source(exam))

    faculty_table = select_table(sections, "faculty", "assigned program", "designation")
    builder.set("faculty_section.faculty_heading", faculty["heading"] if faculty else None, _source(faculty))
    builder.set("faculty_section.faculty_description", html_or_text(faculty), _source(faculty))
    builder.set("faculty_section.faculty_members", _faculty_rows(faculty_table), _source(faculty), 0.95)

    placement_services, recruiters = _placement_clusters(sections, placement)
    builder.set("placement_section.placement_heading", placement["heading"] if placement else None, _source(placement))
    builder.set("placement_section.placement_services", placement_services, _source(placement), 0.9)
    builder.set("placement_section.recruiters", recruiters, _source(placement), 0.9)

    builder.set("reviews_section.reviews_heading", reviews["heading"] if reviews else None, _source(reviews))
    builder.set("reviews_section.reviews", _review_rows(reviews["text"] if reviews else ""), _source(reviews), 0.85)

    builder.set("faq_section.faq_heading", faq["heading"] if faq else None, _source(faq))
    builder.set("faq_section.faqs", _faq_rows(sections), _source(faq), 0.95)

    builder.set("seo_section.meta_title", hero_title, page_title, 0.9)
    builder.set("seo_section.meta_description", _plain_first_sentence(hero or about), _source(hero or about), 0.8)


def _quick_facts(sections: list[dict]) -> list[dict]:
    rows = []
    for section in sections:
        heading = section["heading"]
        if re.search(r"established year\s*-", heading, re.I):
            rows.append({"fact_label": "Established Year", "fact_value": heading.split("-", 1)[1].strip()})
        elif re.search(r"mode of learning\s*-", heading, re.I):
            rows.append({"fact_label": "Mode of Learning", "fact_value": heading.split("-", 1)[1].strip()})
        elif heading.lower() == "amity online detail":
            for line in lines(section["text"]):
                if "-" in line:
                    label, value = [part.strip() for part in line.split("-", 1)]
                    rows.append({"fact_label": label, "fact_value": value})
    return rows


def _hero_badges(detail: dict | None, accreditation: dict | None) -> list[dict]:
    names = []
    if detail:
        names.extend(_known_entities(detail["text"]))
    if accreditation:
        names.extend(_known_entities(accreditation["text"]))
    seen = set()
    badges = []
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        badges.append({"badge_label": name, "badge_type": "accreditation"})
    return badges[:6]


def _points(section: dict | None, title_key: str, description_key: str) -> list[dict]:
    if not section:
        return []
    items = []
    for line in lines(section["text"]):
        if not line:
            continue
        if " - " in line:
            title, description = [part.strip() for part in line.split(" - ", 1)]
        elif ":" in line:
            title, description = [part.strip() for part in line.split(":", 1)]
        else:
            title, description = line, line
        items.append({title_key: title, description_key: html_from_text(description)})
    return items


def _accreditation_rows(text: str) -> list[dict]:
    rows = []
    for name in _known_entities(text):
        rows.append({"accreditation_name": name, "accreditation_subtitle": None})
    return rows


def _program_options(table: list[list[str]] | None) -> list[dict]:
    if not table:
        return []
    return [{"program_name": row[0].strip()} for row in table[1:] if row and row[0].strip()]


def _program_rows(table: list[list[str]] | None) -> list[dict]:
    if not table:
        return []
    rows = []
    for row in table[1:]:
        if not row or not any(cell.strip() for cell in row):
            continue
        rows.append(
            {
                "program_name": row[0].strip() or None,
                "program_subtitle": None,
                "program_fee": row[1].strip() or None if len(row) > 1 else None,
                "program_eligibility": html_from_text(row[2]) if len(row) > 2 and row[2].strip() else None,
            }
        )
    return rows


def _interest_rate(text: str) -> str | None:
    if re.search(r"zero[- ]cost|no[- ]cost", text, re.I):
        return "0%"
    return None


def _tenures(text: str) -> list[dict]:
    matches = re.findall(r"(\d{1,2})[- ]?month", text, re.I)
    return [{"months": f"{match} months"} for match in dict.fromkeys(matches)]


def _emi_features(section: dict | None) -> list[dict]:
    if not section:
        return []
    features = []
    text = section["text"]
    if re.search(r"no[- ]cost", text, re.I):
        features.append({"feature_text": "No-cost EMI available"})
    if re.search(r"loan", text, re.I):
        features.append({"feature_text": "Education loan support"})
    if re.search(r"tie[- ]ups? with renowned banking institutions", text, re.I):
        features.append({"feature_text": "Partner bank tie-ups"})
    return features


def _partner_banks(sections: list[dict]) -> list[str]:
    items = collect_heading_items(sections, ["emi"], ["examination process", "courses", "faculty", "placement", "faq", "review"])
    output = []
    for item in items:
        if re.search(r"bank|hsbc|sbi", item, re.I):
            output.append(item)
    return output


def _faculty_rows(table: list[list[str]] | None) -> list[dict]:
    if not table:
        return []
    output = []
    for row in table[1:]:
        if not row or not row[0].strip():
            continue
        output.append(
            {
                "faculty_name": row[0].strip(),
                "faculty_program": row[1].strip() if len(row) > 1 and row[1].strip() else None,
                "faculty_designation": html_from_text(row[2]) if len(row) > 2 and row[2].strip() else None,
            }
        )
    return output


def _placement_clusters(sections: list[dict], placement: dict | None) -> tuple[list[dict], list[dict]]:
    if not placement:
        return [], []
    service_rows = []
    recruiter_rows = []
    after_placement = collect_heading_items(sections, ["placement"], ["faq", "review"])
    recruiter_mode = False
    for item in after_placement:
        if re.search(r"metlif|samsung|nokia|ibm|google|genpact|spicejet|microsoft", item, re.I):
            recruiter_mode = True
        if recruiter_mode:
            recruiter_rows.append({"recruiter_name": item.replace(", etc", "").strip()})
        else:
            service_rows.append({"service_title": item, "service_description": None})
    return service_rows, recruiter_rows


def _review_rows(text: str) -> list[dict]:
    output = []
    for line in lines(text):
        if not line:
            continue
        output.append({"review_text": html_from_text(line), "review_author": None, "review_rating": None})
    return output


def _faq_rows(sections: list[dict]) -> list[dict]:
    rows = []
    faq_started = False
    for section in sections:
        heading = section["heading"]
        lower = heading.lower()
        if "faq" in lower:
            faq_started = True
            if section["text"].strip():
                rows.extend(extract_faqs(section["text"]))
            continue
        if not faq_started:
            continue
        if "review" in lower:
            break
        if heading.endswith("?"):
            rows.append({"question": heading, "answer": html_from_text(section["text"])})
    return rows


def _known_entities(text: str) -> list[str]:
    entities = [
        "UGC",
        "AICTE",
        "WASC",
        "WES",
        "NAAC A+",
        "NIRF",
        "QS",
        "DEC",
    ]
    found = []
    for entity in entities:
        if re.search(rf"\b{re.escape(entity)}\b", text, re.I):
            found.append(entity)
    return found


def _simple_rows(values: list[str], key: str) -> list[dict]:
    return [{key: value} for value in values if value]


def _plain_first_sentence(section: dict | None) -> str | None:
    if not section:
        return None
    sentences = re.split(r"(?<=[.!?])\s+", section["text"].strip())
    return sentences[0] if sentences and sentences[0] else None


def _source(section: dict | None) -> str | None:
    return section["heading"] if section else None
