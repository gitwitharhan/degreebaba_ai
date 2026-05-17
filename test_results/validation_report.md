# DegreeBaba AI Pipeline — Batch Test & Validation Report

This document summarizes the validation metrics and pipeline integrity check for at least 2 Word documents per page type (6 files total).

## 1. Batch Execution Summary Table

| Test ID | File Name | Classified Page Type | Class. Confidence | Missing Fields | Thin Content | Warnings |
| --- | --- | --- | --- | --- | --- | --- |
| **university_1** | `university_1.docx` | University | 0.98 | 0 | 0 | 4 |
| **university_2** | `university_2.docx` | University | 0.98 | 0 | 0 | 5 |
| **course_1** | `course_1.docx` | Course | 0.98 | 0 | 0 | 12 |
| **course_2** | `course_2.docx` | Course | 0.98 | 0 | 0 | 11 |
| **specialization_1** | `specialization_1.docx` | Specialization | 0.98 | 0 | 0 | 9 |
| **specialization_2** | `specialization_2.docx` | Specialization | 0.98 | 0 | 0 | 9 |

## 2. Field-Level Validation Failures & Warnings

### Test Run: university_1
- **File:** `university_1.docx`
- **Classified Type:** UNIVERSITY (Confidence: 0.98)
- **Missing Fields:** None (100% complete)
- **Pipeline Warnings:**
  - *Incomplete repeater 'accreditation_section.accreditations': Missing attributes ['accreditation_subtitle']*
  - *Incomplete repeater 'programs_section.programs': Missing attributes ['program_subtitle']*
  - *Incomplete repeater 'placement_section.placement_services': Missing attributes ['service_description']*
  - *Incomplete repeater 'reviews_section.reviews': Missing attributes ['review_rating', 'review_author']*

---

### Test Run: university_2
- **File:** `university_2.docx`
- **Classified Type:** UNIVERSITY (Confidence: 0.98)
- **Missing Fields:** None (100% complete)
- **Pipeline Warnings:**
  - *Incomplete repeater 'accreditation_section.accreditations': Missing attributes ['accreditation_subtitle']*
  - *Incomplete repeater 'programs_section.programs': Missing attributes ['program_subtitle']*
  - *Incomplete repeater 'placement_section.placement_services': Missing attributes ['service_description']*
  - *Incomplete repeater 'reviews_section.reviews': Missing attributes ['review_rating', 'review_author']*
  - *AI review failed: Groq HTTP error 429: {"error":{"message":"Rate limit reached for model `qwen/qwen3-32b` in organization `org_01kp84jgvge5xs0nywv9prd1cc` service tier `on_demand` on tokens per minute (TPM): Limit 6000, Used 5212, Requested 2517. Please try again in 17.29s. Need more tokens? Upgrade to Dev Tier today at https://console.g*

---

### Test Run: course_1
- **File:** `course_1.docx`
- **Classified Type:** COURSE (Confidence: 0.98)
- **Missing Fields:** None (100% complete)
- **Pipeline Warnings:**
  - *breadcrumb_section.breadcrumbs must be an array*
  - *Incomplete repeater 'hero_section.hero_badges': Missing attributes ['badge_variant', 'badge_icon']*
  - *Incomplete repeater 'hero_section.hero_stats': Missing attributes ['stat_suffix']*
  - *Incomplete repeater 'overview_section.overview_cards': Missing attributes ['color_variant']*
  - *Incomplete repeater 'highlights_section.highlights': Missing attributes ['icon']*
  - *Incomplete repeater 'accreditation_section.accreditations': Missing attributes ['description', 'color_variant']*
  - *Incomplete repeater 'specialization_section.specializations': Missing attributes ['icon_bg_variant', 'icon']*
  - *Incomplete repeater 'fee_structure_section.fee_plans': Missing attributes ['billing_frequency', 'total_fee', 'savings_text']*
  - *Incomplete repeater 'placement_section.recruiters': Missing attributes ['company_logo']*
  - *Incomplete repeater 'job_roles_section.job_roles': Missing attributes ['salary_growth_percentage']*
  - *Incomplete repeater 'reviews_section.reviews': Missing attributes ['rating', 'designation', 'student_name']*
  - *AI review failed: Groq HTTP error 429: {"error":{"message":"Rate limit reached for model `qwen/qwen3-32b` in organization `org_01kp84jgvge5xs0nywv9prd1cc` service tier `on_demand` on tokens per minute (TPM): Limit 6000, Used 5270, Requested 2807. Please try again in 20.77s. Need more tokens? Upgrade to Dev Tier today at https://console.g*

---

### Test Run: course_2
- **File:** `course_2.docx`
- **Classified Type:** COURSE (Confidence: 0.98)
- **Missing Fields:** None (100% complete)
- **Pipeline Warnings:**
  - *Incomplete repeater 'hero_section.hero_badges': Missing attributes ['badge_variant', 'badge_icon']*
  - *Incomplete repeater 'hero_section.hero_stats': Missing attributes ['stat_suffix']*
  - *Incomplete repeater 'overview_section.overview_cards': Missing attributes ['color_variant']*
  - *Incomplete repeater 'highlights_section.highlights': Missing attributes ['icon']*
  - *Incomplete repeater 'accreditation_section.accreditations': Missing attributes ['description', 'color_variant']*
  - *Incomplete repeater 'specialization_section.specializations': Missing attributes ['icon_bg_variant', 'icon']*
  - *Incomplete repeater 'fee_structure_section.fee_plans': Missing attributes ['billing_frequency', 'total_fee', 'savings_text']*
  - *Incomplete repeater 'placement_section.recruiters': Missing attributes ['company_logo']*
  - *Incomplete repeater 'job_roles_section.job_roles': Missing attributes ['salary_growth_percentage']*
  - *Incomplete repeater 'reviews_section.reviews': Missing attributes ['rating', 'designation', 'student_name']*
  - *AI review failed: Groq HTTP error 429: {"error":{"message":"Rate limit reached for model `qwen/qwen3-32b` in organization `org_01kp84jgvge5xs0nywv9prd1cc` service tier `on_demand` on tokens per minute (TPM): Limit 6000, Used 5157, Requested 2653. Please try again in 18.1s. Need more tokens? Upgrade to Dev Tier today at https://console.gr*

---

### Test Run: specialization_1
- **File:** `specialization_1.docx`
- **Classified Type:** SPECIALIZATION (Confidence: 0.98)
- **Missing Fields:** None (100% complete)
- **Pipeline Warnings:**
  - *Incomplete repeater 'hero_section.hero_badges': Missing attributes ['badge_variant']*
  - *Incomplete repeater 'hero_section.hero_stats': Missing attributes ['stat_suffix']*
  - *Incomplete repeater 'fee_structure_section.fee_plans': Missing attributes ['amount', 'savings_text']*
  - *Incomplete repeater 'syllabus_section.years': Missing attributes ['semesters']*
  - *Incomplete repeater 'placement_section.placement_services': Missing attributes ['service_description']*
  - *Incomplete repeater 'reviews_section.reviews': Missing attributes ['rating', 'review_author']*
  - *Incomplete repeater 'sidebar_section.at_a_glance': Missing attributes ['value_variant']*
  - *Duplicate stat values detected: 100%, 21, 24, 46%*
  - *AI review failed: Groq HTTP error 429: {"error":{"message":"Rate limit reached for model `qwen/qwen3-32b` in organization `org_01kp84jgvge5xs0nywv9prd1cc` service tier `on_demand` on tokens per minute (TPM): Limit 6000, Used 5447, Requested 2960. Please try again in 24.07s. Need more tokens? Upgrade to Dev Tier today at https://console.g*

---

### Test Run: specialization_2
- **File:** `specialization_2.docx`
- **Classified Type:** SPECIALIZATION (Confidence: 0.98)
- **Missing Fields:** None (100% complete)
- **Pipeline Warnings:**
  - *Incomplete repeater 'hero_section.hero_badges': Missing attributes ['badge_variant']*
  - *Incomplete repeater 'hero_section.hero_stats': Missing attributes ['stat_suffix']*
  - *Incomplete repeater 'fee_structure_section.fee_plans': Missing attributes ['amount', 'savings_text']*
  - *Incomplete repeater 'syllabus_section.years': Missing attributes ['semesters']*
  - *Incomplete repeater 'placement_section.placement_services': Missing attributes ['service_description']*
  - *Incomplete repeater 'reviews_section.reviews': Missing attributes ['rating', 'review_author']*
  - *Incomplete repeater 'sidebar_section.at_a_glance': Missing attributes ['value_variant']*
  - *Duplicate stat values detected: 100%, 21, 24, 46%*
  - *AI review failed: Groq HTTP error 429: {"error":{"message":"Rate limit reached for model `qwen/qwen3-32b` in organization `org_01kp84jgvge5xs0nywv9prd1cc` service tier `on_demand` on tokens per minute (TPM): Limit 6000, Used 5493, Requested 2960. Please try again in 24.53s. Need more tokens? Upgrade to Dev Tier today at https://console.g*

---

