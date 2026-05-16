from __future__ import annotations

import re

from backend.mapper.base_mapper import MappingBuilder
from backend.mapper.content_utils import (
    collect_heading_items,
    extract_faqs,
    extract_steps,
    extract_stats,
    find_section,
    html_from_text,
    html_or_text,
    lines,
    select_table,
)
from backend.mapper.fuzzy_mapper import slug


def map_specialization(builder: MappingBuilder, sections: list[dict], raw_text: str) -> None:
    title = sections[0]["heading"] if sections else None
    details = find_section(sections, "course details")
    facts = find_section(sections, "course facts")
    eligibility = find_section(sections, "eligibility")
    fees = find_section(sections, "specialization fee")
    admission = find_section(sections, "admission process")
    certificate = find_section(sections, "sample certificate")
    emi = find_section(sections, "emi")
    syllabus = find_section(sections, "syllabus")
    exam = find_section(sections, "examination")
    placement = find_section(sections, "placement")
    faq = find_section(sections, "faq")
    reviews = find_section(sections, "reviews")

    comparison_table = select_table(sections, "specialization", "course fee")
    syllabus_table = select_table(sections, "year i", "semester i")

    specialization_name = _extract_specialization_name(title or "")
    course_name = "MBA" if title and "mba" in title.lower() else None
    university_name = _extract_university_name(raw_text)

    builder.set("specialization_name", specialization_name, title, 1.0)
    builder.set("specialization_slug", slug(specialization_name or ""), title, 0.95)
    builder.set("course_name", course_name, title, 0.9)
    builder.set("course_slug", slug(course_name or ""), title, 0.85)
    builder.set("specialization_type", "MBA Specialization" if course_name else None, title, 0.85)
    builder.set("delivery_mode", "Online" if "online" in raw_text.lower() else None, "raw_text", 0.9)
    _set_duration(builder, raw_text)

    builder.set("university.university_name", university_name, title, 0.95)
    builder.set("university.university_slug", slug(university_name or ""), title, 0.9)
    builder.set("university.approval_bodies", _approval_rows(raw_text), "raw_text", 0.85)

    builder.set("hero_section.specialization_tag", title, title, 0.9)
    builder.set("hero_section.headline", title, title, 1.0)
    builder.set("hero_section.highlight_text", specialization_name, title, 0.85)
    builder.set("hero_section.university_name", university_name, title, 0.95)
    builder.set("hero_section.hero_description", html_or_text(details), _source(details))
    builder.set("hero_section.hero_badges", _hero_badges(raw_text), "raw_text", 0.85)
    builder.set("hero_section.hero_stats", _hero_stats(raw_text), "raw_text", 0.9)

    builder.set("lead_form_section.form_heading", None, None)
    builder.set("lead_form_section.form_description", None, None)

    builder.set("overview_section.heading", details["heading"] if details else None, _source(details))
    builder.set("overview_section.content", html_or_text(details), _source(details))
    builder.set("overview_section.overview_stats", _overview_stats(raw_text), "raw_text", 0.85)
    builder.set("overview_section.program_benefits", _program_benefits(facts), _source(facts), 0.9)

    builder.set("program_highlights_section.heading", facts["heading"] if facts else None, _source(facts))
    builder.set("program_highlights_section.highlights", _highlights(facts), _source(facts), 0.9)

    builder.set("eligibility_section.heading", eligibility["heading"] if eligibility else None, _source(eligibility))
    builder.set("eligibility_section.eligibility_cards", _eligibility_cards(eligibility), _source(eligibility), 0.95)
    builder.set("eligibility_section.eligibility_note", html_or_text(find_section(sections, "additional information")), "Additional information")

    builder.set("fee_structure_section.heading", fees["heading"] if fees else None, _source(fees))
    builder.set("fee_structure_section.fee_plans", _fee_plans(comparison_table, specialization_name), _source(fees), 0.95)

    builder.set("emi_section.feature_tag", "EMI" if emi else None, _source(emi), 0.8)
    builder.set("emi_section.emi_heading", emi["heading"] if emi else None, _source(emi))
    builder.set("emi_section.emi_description", html_or_text(emi), _source(emi))
    builder.set("emi_section.starting_emi", _starting_emi(emi["text"] if emi else raw_text), _source(emi), 0.9)
    builder.set("emi_section.emi_tenures", _tenures(emi["text"] if emi else raw_text), _source(emi), 0.9)
    builder.set("emi_section.emi_features", _emi_features(emi), _source(emi), 0.85)

    builder.set("partner_banks_section.heading", None, None)
    builder.set("partner_banks_section.subheading", None, None)
    builder.set("partner_banks_section.partner_banks", [], None)

    builder.set("specialization_comparison_section.heading", fees["heading"] if fees else None, _source(fees))
    builder.set("specialization_comparison_section.specializations", _comparison_rows(comparison_table, specialization_name), _source(fees), 0.95)

    builder.set("syllabus_section.heading", syllabus["heading"] if syllabus else None, _source(syllabus))
    builder.set("syllabus_section.years", _syllabus_years(syllabus_table), _source(syllabus), 0.95)

    builder.set("exam_section.heading", exam["heading"] if exam else None, _source(exam))
    builder.set("exam_section.description", html_or_text(exam), _source(exam))
    builder.set("exam_section.exam_cards", _exam_cards(exam), _source(exam), 0.85)

    builder.set("admission_section.heading", admission["heading"] if admission else None, _source(admission))
    builder.set("admission_section.steps", extract_steps(admission["text"]) if admission else [], _source(admission), 0.95)

    placement_services, recruiters = _placement_rows(sections, placement)
    builder.set("placement_section.heading", placement["heading"] if placement else None, _source(placement))
    builder.set("placement_section.placement_stats", _placement_stats(raw_text), "raw_text", 0.85)
    builder.set("placement_section.placement_services", placement_services, _source(placement), 0.9)
    builder.set("placement_section.recruiters", recruiters, _source(placement), 0.9)

    builder.set("certificate_section.certificate_title", certificate["heading"] if certificate else None, _source(certificate))
    builder.set("certificate_section.certificate_description", html_or_text(certificate), _source(certificate))

    builder.set("reviews_section.heading", reviews["heading"] if reviews else None, _source(reviews))
    builder.set("reviews_section.reviews", _review_rows(reviews["text"] if reviews else ""), _source(reviews), 0.85)

    builder.set("faq_section.heading", faq["heading"] if faq else None, _source(faq))
    builder.set("faq_section.faq_items", _faq_rows(sections), _source(faq), 0.95)

    builder.set("sidebar_section.quick_links", _quick_links(sections), "sections", 0.8)
    builder.set("sidebar_section.at_a_glance", _at_a_glance(raw_text, specialization_name), "raw_text", 0.8)

    builder.set("seo_section.meta_title", title, title, 0.9)
    builder.set("seo_section.meta_description", _plain_text(details), _source(details), 0.85)
    builder.set("seo_section.focus_keyword", specialization_name, title, 0.8)


def _extract_specialization_name(title: str) -> str | None:
    match = re.search(r"\bMBA\s+in\s+(.+)", title, re.I)
    return match.group(1).strip() if match else title or None


def _extract_university_name(text: str) -> str | None:
    match = re.search(r"(Amity University Online)", text, re.I)
    return match.group(1) if match else None


def _set_duration(builder: MappingBuilder, raw_text: str) -> None:
    if match := re.search(r"\b(\d+)\s*year", raw_text, re.I):
        builder.set("duration.duration_value", match.group(1), "raw_text", 0.9)
        builder.set("duration.duration_unit", "Years", "raw_text", 0.9)
    elif match := re.search(r"\b(\d+)\s*month", raw_text, re.I):
        builder.set("duration.duration_value", match.group(1), "raw_text", 0.9)
        builder.set("duration.duration_unit", "Months", "raw_text", 0.9)


def _approval_rows(text: str) -> list[dict]:
    rows = []
    for name in ["UGC", "WES", "WASC", "NAAC", "AICTE", "NIRF"]:
        if re.search(rf"\b{re.escape(name)}\b", text, re.I):
            rows.append({"approval_name": name, "approval_logo": None})
    return rows


def _hero_badges(text: str) -> list[dict]:
    rows = []
    for badge in ["Online", "QS Ranked", "MBA", "Data Science"]:
        if badge.lower() in text.lower():
            rows.append({"badge_text": badge, "badge_variant": None})
    return rows


def _hero_stats(text: str) -> list[dict]:
    stats = extract_stats(text, value_key="stat_value", label_key="stat_label")
    for item in stats:
        value = item.get("stat_value")
        if isinstance(value, str):
            match = re.match(r"(\d+(?:\.\d+)?)(.*)", value)
            item["stat_value"] = match.group(1) if match else value
            item["stat_suffix"] = match.group(2) if match else None
    return stats


def _overview_stats(text: str) -> list[dict]:
    return extract_stats(text, value_key="stat_value", label_key="stat_label", limit=4)


def _program_benefits(section: dict | None) -> list[dict]:
    if not section:
        return []
    return [{"benefit_title": line, "benefit_description": html_from_text(line)} for line in lines(section["text"]) if line]


def _highlights(section: dict | None) -> list[dict]:
    if not section:
        return []
    return [{"title": line, "description": html_from_text(line)} for line in lines(section["text"]) if line]


def _eligibility_cards(section: dict | None) -> list[dict]:
    if not section:
        return []
    return [{"criteria_title": line, "criteria_description": html_from_text(line)} for line in lines(section["text"]) if line]


def _fee_plans(table: list[list[str]] | None, specialization_name: str | None) -> list[dict]:
    if not table:
        return []
    rows = []
    for row in table[1:]:
        if not row or not row[0].strip():
            continue
        rows.append(
            {
                "plan_name": row[0].strip(),
                "amount": None,
                "frequency_text": "Entire Course Fee",
                "total_fee": row[1].strip() if len(row) > 1 and row[1].strip() else None,
                "savings_text": None,
                "is_best_value": specialization_name and specialization_name.lower() in row[0].lower(),
            }
        )
    return rows


def _comparison_rows(table: list[list[str]] | None, specialization_name: str | None) -> list[dict]:
    if not table:
        return []
    rows = []
    for row in table[1:]:
        if not row or not row[0].strip():
            continue
        rows.append(
            {
                "specialization_name": row[0].strip(),
                "specialization_fee": row[1].strip() if len(row) > 1 and row[1].strip() else None,
                "is_active_specialization": specialization_name and specialization_name.lower() in row[0].lower(),
            }
        )
    return rows


def _starting_emi(text: str) -> str | None:
    match = re.search(r"INR\s*([0-9,]+)\s*/-", text, re.I)
    return f"INR {match.group(1)} /-" if match else None


def _tenures(text: str) -> list[dict]:
    matches = re.findall(r"(\d{1,2})[- ]?month", text, re.I)
    return [{"months": f"{month} months", "is_featured": index == 0} for index, month in enumerate(dict.fromkeys(matches))]


def _emi_features(section: dict | None) -> list[dict]:
    if not section:
        return []
    text = section["text"]
    features = []
    if re.search(r"zero-cost|no-cost", text, re.I):
        features.append({"feature_text": "Zero-cost EMI"})
    if re.search(r"financial difficulties", text, re.I):
        features.append({"feature_text": "Financial support for eligible students"})
    return features


def _syllabus_years(table: list[list[str]] | None) -> list[dict]:
    if not table or len(table) < 3:
        return []
    year_name = table[1][0].strip() if table[1] and table[1][0].strip() else "Year I"
    semesters = []
    for row in table[2:]:
        if len(row) >= 2:
            left = row[0].strip()
            right = row[1].strip()
            if left.startswith("Semester"):
                semesters.append({"semester_name": left, "subjects": []})
            if right.startswith("Semester"):
                semesters.append({"semester_name": right, "subjects": []})
    return [{"year_name": year_name, "semesters": semesters}]


def _exam_cards(section: dict | None) -> list[dict]:
    if not section:
        return []
    cards = []
    for sentence in re.split(r"(?<=[.!?])\s+", section["text"]):
        sentence = sentence.strip()
        if not sentence:
            continue
        title = sentence.split(",", 1)[0][:80]
        cards.append({"card_title": title, "card_description": html_from_text(sentence)})
    return cards[:3]


def _placement_rows(sections: list[dict], placement: dict | None) -> tuple[list[dict], list[dict]]:
    if not placement:
        return [], []
    recruiters = [{"company_name": name} for name in collect_heading_items(sections, ["placement"], ["faq", "review"])]
    services = []
    for phrase in ["resume-building", "interview preparation", "profile-building", "career coach", "virtual job fairs"]:
        if phrase in placement["text"].lower():
            services.append({"service_title": phrase.title(), "service_description": None})
    return services, recruiters


def _placement_stats(text: str) -> list[dict]:
    return extract_stats(text, value_key="stat_value", label_key="stat_label", limit=3)


def _review_rows(text: str) -> list[dict]:
    return [{"review_text": html_from_text(line), "review_author": None, "rating": None} for line in lines(text) if line]


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


def _quick_links(sections: list[dict]) -> list[dict]:
    links = []
    for section in sections[1:10]:
        if section["heading"] and section["heading"] != "Document Start":
            links.append({"label": section["heading"], "anchor_id": slug(section["heading"])})
    return links


def _at_a_glance(text: str, specialization_name: str | None) -> list[dict]:
    rows = []
    if specialization_name:
        rows.append({"label": "Specialization", "value": specialization_name, "value_variant": None})
    if "online" in text.lower():
        rows.append({"label": "Mode", "value": "Online", "value_variant": None})
    if match := re.search(r"\b(\d+)\s*year", text, re.I):
        rows.append({"label": "Duration", "value": f"{match.group(1)} Years", "value_variant": None})
    return rows


def _plain_text(section: dict | None) -> str | None:
    if not section:
        return None
    return section["text"].strip() or None


def _source(section: dict | None) -> str | None:
    return section["heading"] if section else None
