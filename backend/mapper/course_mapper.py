from __future__ import annotations

import re

from backend.mapper.base_mapper import MappingBuilder
from backend.mapper.content_utils import (
    collect_heading_items,
    extract_faqs,
    extract_steps,
    extract_stats,
    find_section,
    first_non_empty_line,
    html_from_text,
    html_or_text,
    lines,
    select_table,
)
from backend.mapper.fuzzy_mapper import slug


def map_course(builder: MappingBuilder, sections: list[dict], raw_text: str) -> None:
    first_heading = sections[0]["heading"] if sections else None
    alt_heading = sections[1]["heading"] if len(sections) > 1 else None
    meta = find_section(sections, "meta description")
    about = find_section(sections, "about", "course")
    facts = find_section(sections, "course facts")
    accreditations = find_section(sections, "accreditations")
    eligibility = find_section(sections, "eligibility")
    admission = find_section(sections, "admission process")
    specializations = find_section(sections, "specializations offered")
    fee_structure = find_section(sections, "fee structure")
    syllabus = find_section(sections, "syllabus", "curriculum")
    placement = find_section(sections, "placement partners", "placement")
    jobs = find_section(sections, "job roles", "salary")
    certificate = find_section(sections, "sample certificate")
    reviews = find_section(sections, "reviews")
    faq = find_section(sections, "faq")

    hero_stats = _course_stats(raw_text)
    specializations_table = select_table(sections, "specializations", "course fee")
    semester_fee_table = select_table(sections, "semester", "fee")
    syllabus_table = select_table(sections, "semester i", "semester ii")
    job_table = select_table(sections, "job prospects", "average salary")

    course_name = first_non_empty_line(first_heading or "")
    university_name = _extract_university_name(raw_text)

    builder.set("course_name", course_name, first_heading, 1.0)
    builder.set("course_slug", slug(course_name or ""), first_heading, 0.95)
    builder.set("course_type", "MBA" if course_name and "mba" in course_name.lower() else None, first_heading, 0.9)
    builder.set("degree_level", "Postgraduate" if course_name and "mba" in course_name.lower() else None, first_heading, 0.9)
    builder.set("delivery_mode", "Online" if "online" in raw_text.lower() else None, "raw_text", 0.9)
    _set_duration(builder, raw_text)

    builder.set("university.university_name", university_name, first_heading, 0.95)
    builder.set("university.university_slug", slug(university_name or ""), first_heading, 0.9)
    builder.set(
        "university.approval_bodies",
        _approval_bodies(accreditations["text"] if accreditations else raw_text),
        _source(accreditations),
        0.9,
    )

    builder.set("hero_section.program_tag", alt_heading, alt_heading, 0.9)
    builder.set("hero_section.headline", course_name, first_heading, 1.0)
    builder.set("hero_section.highlight_text", alt_heading, alt_heading, 0.8)
    builder.set("hero_section.subheading", meta["text"] if meta else _plain_text(about), _source(meta or about), 0.9)
    builder.set("hero_section.hero_badges", _badge_rows(accreditations, facts), _source(accreditations or facts), 0.85)
    builder.set("hero_section.hero_stats", hero_stats, "raw_text", 0.95)

    builder.set("overview_section.heading", about["heading"] if about else None, _source(about))
    builder.set("overview_section.description", html_or_text(about), _source(about))
    builder.set("overview_section.overview_cards", _overview_cards(raw_text), "raw_text", 0.85)

    builder.set("highlights_section.heading", facts["heading"] if facts else None, _source(facts))
    builder.set("highlights_section.highlights", _highlights(facts), _source(facts), 0.9)

    builder.set("accreditation_section.heading", accreditations["heading"] if accreditations else None, _source(accreditations))
    builder.set(
        "accreditation_section.accreditations",
        _accreditation_rows(accreditations["text"] if accreditations else raw_text),
        _source(accreditations),
        0.9,
    )

    builder.set("specialization_section.heading", specializations["heading"] if specializations else None, _source(specializations))
    builder.set("specialization_section.description", _plain_text(specializations), _source(specializations))
    builder.set("specialization_section.specializations", _specialization_rows(specializations_table), _source(specializations), 0.95)

    builder.set("fee_structure_section.heading", fee_structure["heading"] if fee_structure else None, _source(fee_structure))
    builder.set("fee_structure_section.fee_plans", _fee_plans(semester_fee_table), _source(fee_structure), 0.95)

    builder.set("emi_section.feature_tag", "EMI" if fee_structure or facts else None, _source(fee_structure or facts), 0.8)
    builder.set("emi_section.heading", fee_structure["heading"] if fee_structure else None, _source(fee_structure))
    builder.set("emi_section.description", _plain_text(fee_structure), _source(fee_structure))
    builder.set("emi_section.starting_emi", _starting_emi(raw_text), "raw_text", 0.9)
    builder.set("emi_section.tenures", _tenures(raw_text), "raw_text", 0.9)
    builder.set("emi_section.benefits", _emi_benefits(facts, fee_structure), _source(facts or fee_structure), 0.85)

    builder.set("partner_banks_section.heading", None, None)
    builder.set("partner_banks_section.subheading", None, None)
    builder.set("partner_banks_section.banks", [], None)

    builder.set("scholarship_section.heading", None, None)
    builder.set("scholarship_section.description", None, None)

    builder.set("syllabus_section.heading", syllabus["heading"] if syllabus else None, _source(syllabus))
    builder.set("syllabus_section.years", _syllabus_years(syllabus_table), _source(syllabus), 0.95)

    builder.set("eligibility_section.heading", eligibility["heading"] if eligibility else None, _source(eligibility))
    builder.set("eligibility_section.eligibility_cards", _eligibility_cards(eligibility), _source(eligibility), 0.95)

    builder.set("admission_process_section.heading", admission["heading"] if admission else None, _source(admission))
    builder.set("admission_process_section.steps", extract_steps(admission["text"]) if admission else [], _source(admission), 0.95)

    placement_services, recruiters = _course_placement(sections, placement)
    builder.set("placement_section.heading", placement["heading"] if placement else None, _source(placement))
    builder.set("placement_section.placement_services", placement_services, _source(placement), 0.9)
    builder.set("placement_section.recruiters", recruiters, _source(placement), 0.9)

    builder.set("job_roles_section.heading", jobs["heading"] if jobs else None, _source(jobs))
    builder.set("job_roles_section.job_roles", _job_rows(job_table), _source(jobs), 0.95)

    builder.set("reviews_section.heading", reviews["heading"] if reviews else None, _source(reviews))
    builder.set("reviews_section.reviews", _review_rows(reviews["text"] if reviews else ""), _source(reviews), 0.85)

    builder.set("faq_section.heading", faq["heading"] if faq else None, _source(faq))
    builder.set("faq_section.faq_items", _faq_rows(sections), _source(faq), 0.95)

    builder.set("seo_section.meta_title", course_name, first_heading, 0.9)
    builder.set("seo_section.meta_description", meta["text"] if meta else _plain_text(about), _source(meta or about), 0.85)
    builder.set("seo_section.focus_keyword", course_name, first_heading, 0.8)
    builder.set("certificate_section.heading", certificate["heading"] if certificate else None, _source(certificate))


def _set_duration(builder: MappingBuilder, raw_text: str) -> None:
    year_match = re.search(r"\b(\d+)\s*year\b", raw_text, re.I)
    month_match = re.search(r"\b(\d+)\s*month\b", raw_text, re.I)
    if year_match:
        builder.set("duration.duration_value", year_match.group(1), "raw_text", 0.9)
        builder.set("duration.duration_unit", "Years", "raw_text", 0.9)
    elif month_match:
        builder.set("duration.duration_value", month_match.group(1), "raw_text", 0.9)
        builder.set("duration.duration_unit", "Months", "raw_text", 0.9)


def _extract_university_name(text: str) -> str | None:
    match = re.search(r"(Amity University Online)", text, re.I)
    return match.group(1) if match else None


def _approval_bodies(text: str) -> list[dict]:
    rows = []
    for short, _full_name in _known_approvals():
        if re.search(rf"\b{re.escape(short)}\b", text, re.I) or _full_name.lower() in text.lower():
            rows.append({"approval_name": short, "approval_logo": None})
    return rows


def _accreditation_rows(text: str) -> list[dict]:
    names = []
    for short, full_name in _known_approvals():
        if re.search(rf"\b{re.escape(short)}\b", text, re.I) or full_name.lower() in text.lower():
            names.append({"short_name": short, "full_name": full_name, "description": None, "color_variant": None})
    return names


def _known_approvals() -> list[tuple[str, str]]:
    return [
        ("UGC", "University Grants Commission"),
        ("WES", "World Education Services"),
        ("WASC", "Western Association of Schools and Colleges"),
        ("NAAC", "National Assessment and Accreditation Council"),
        ("AICTE", "All India Council for Technical Education"),
        ("NIRF", "National Institutional Ranking Framework"),
        ("DEC", "Digital Education Council"),
    ]


def _badge_rows(accreditations: dict | None, facts: dict | None) -> list[dict]:
    rows = []
    for name in ["UGC", "NAAC A+", "WES", "WASC", "QS Ranked"]:
        corpus = f"{accreditations['text'] if accreditations else ''}\n{facts['text'] if facts else ''}"
        if re.search(re.escape(name.replace(" A+", "")), corpus, re.I):
            rows.append({"badge_text": name, "badge_variant": None, "badge_icon": None})
    return rows


def _course_stats(raw_text: str) -> list[dict]:
    stats = extract_stats(raw_text, value_key="stat_value", label_key="stat_label")
    for item in stats:
        value = item.get("stat_value")
        if isinstance(value, str):
            match = re.match(r"(\d+(?:\.\d+)?)(.*)", value)
            if match:
                item["stat_value"] = match.group(1)
                item["stat_suffix"] = match.group(2) or None
            else:
                item["stat_suffix"] = None
    return stats


def _overview_cards(raw_text: str) -> list[dict]:
    cards = []
    if match := re.search(r"\b(\d+)\s*year", raw_text, re.I):
        cards.append({"value": match.group(1), "label": "Duration (Years)", "color_variant": None})
    if match := re.search(r"(\d+)\s+diverse specializations", raw_text, re.I):
        cards.append({"value": match.group(1), "label": "Specializations", "color_variant": None})
    if match := re.search(r"(\d+)\s*month interest-free", raw_text, re.I):
        cards.append({"value": match.group(1), "label": "EMI Tenure (Months)", "color_variant": None})
    return cards


def _highlights(section: dict | None) -> list[dict]:
    if not section:
        return []
    return [{"title": line, "description": line, "icon": None} for line in lines(section["text"]) if line]


def _specialization_rows(table: list[list[str]] | None) -> list[dict]:
    if not table:
        return []
    rows = []
    for row in table[1:]:
        if not row or not row[0].strip():
            continue
        name = row[0].strip()
        rows.append(
            {
                "specialization_name": name,
                "specialization_slug": slug(name),
                "icon": None,
                "icon_bg_variant": None,
                "fee_text": row[1].strip() if len(row) > 1 and row[1].strip() else None,
                "is_featured": name.lower() == "dual specialization",
            }
        )
    return rows


def _fee_plans(table: list[list[str]] | None) -> list[dict]:
    if not table:
        return []
    rows = []
    for row in table[1:]:
        if not row or not row[0].strip():
            continue
        rows.append(
            {
                "plan_name": row[0].strip(),
                "amount": row[1].strip() if len(row) > 1 and row[1].strip() else None,
                "billing_frequency": "Per Semester" if "semester" in row[0].lower() else None,
                "total_fee": None,
                "savings_text": None,
                "is_highlighted": row[0].strip().lower() == "semester i",
            }
        )
    return rows


def _starting_emi(text: str) -> str | None:
    match = re.search(r"INR\s*([0-9,]+)\s*/-\s*per month", text, re.I)
    return f"INR {match.group(1)} /-" if match else None


def _tenures(text: str) -> list[dict]:
    matches = re.findall(r"(\d{1,2})\s*month", text, re.I)
    return [{"months": f"{month} months", "is_featured": index == 0} for index, month in enumerate(dict.fromkeys(matches))]


def _emi_benefits(facts: dict | None, fee_structure: dict | None) -> list[dict]:
    text = f"{facts['text'] if facts else ''}\n{fee_structure['text'] if fee_structure else ''}"
    benefits = []
    if re.search(r"interest-free", text, re.I):
        benefits.append({"benefit_text": "Interest-free EMI support"})
    if re.search(r"financial aid", text, re.I):
        benefits.append({"benefit_text": "Financial aid available"})
    if re.search(r"semester or annual plan", text, re.I):
        benefits.append({"benefit_text": "Multiple fee payment plans"})
    return benefits


def _syllabus_years(table: list[list[str]] | None) -> list[dict]:
    if not table or len(table) < 2:
        return []
    years = []
    current_year = {"year_name": "Year I", "semesters": []}
    for row in table:
        if len(row) >= 2 and row[0].strip().startswith("Semester") and row[1].strip().startswith("Semester"):
            sem_one = {"semester_name": row[0].strip(), "subjects": []}
            sem_two = {"semester_name": row[1].strip(), "subjects": []}
            current_year["semesters"].extend([sem_one, sem_two])
        elif current_year["semesters"] and len(row) >= 2:
            current_year["semesters"][-2]["subjects"] = [{"subject_name": item.strip()} for item in row[0].splitlines() if item.strip()]
            current_year["semesters"][-1]["subjects"] = [{"subject_name": item.strip()} for item in row[1].splitlines() if item.strip()]
    years.append(current_year)
    return years


def _eligibility_cards(section: dict | None) -> list[dict]:
    if not section:
        return []
    cards = []
    for line in lines(section["text"]):
        cards.append({"title": line, "description": html_from_text(line)})
    return cards


def _course_placement(sections: list[dict], placement: dict | None) -> tuple[list[dict], list[dict]]:
    if not placement:
        return [], []
    recruiters = [{"company_name": name, "company_logo": None} for name in collect_heading_items(sections, ["placement partners"], ["job roles", "faq", "review"])]
    services = []
    for phrase in ["resume-building workshops", "interview preparation", "industry mentorship"]:
        if phrase in placement["text"].lower():
            services.append({"service_text": phrase})
    if not services and placement["text"].strip():
        services.append({"service_text": _plain_text(placement)})
    return services, recruiters


def _job_rows(table: list[list[str]] | None) -> list[dict]:
    if not table:
        return []
    rows = []
    for row in table[1:]:
        if not row or not row[0].strip():
            continue
        rows.append(
            {
                "job_title": row[0].strip(),
                "average_salary": row[1].strip() if len(row) > 1 and row[1].strip() else None,
                "salary_growth_percentage": None,
            }
        )
    return rows


def _review_rows(text: str) -> list[dict]:
    return [
        {"review_text": html_from_text(line), "student_name": None, "rating": None, "designation": None}
        for line in lines(text)
        if line
    ]


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


def _plain_text(section: dict | None) -> str | None:
    if not section:
        return None
    return section["text"].strip() or None


def _source(section: dict | None) -> str | None:
    return section["heading"] if section else None
