# DegreeBaba DOCX to ACF Parser

This project is a content parsing micro app for DegreeBaba.

The goal is simple:

- take a `.docx` file created by a content writer
- understand whether it is a `university`, `course`, or `specialization` page
- map the content into the correct ACF-style JSON structure
- return a final payload plus a validation report

The WordPress publish/update step is intentionally left for the next phase. Right now the product focus is:

1. upload file
2. generate final JSON
3. review validation

## Why this project exists

DegreeBaba pages are built in WordPress using ACF fields, but content writers work in Word documents.

That creates a mapping problem:

- writers use natural headings like `About the University`
- the website needs technical structured fields like `about_content`
- some content is plain text
- some content is structured like FAQs, tables, stats, repeaters, and syllabus blocks
- the output must be safe for WordPress and should avoid fake or missing data

This project bridges that gap.

## What the system does

The system reads a DOCX file and produces a JSON response like this:

```json
{
  "page_type": "university",
  "classification_confidence": 0.96,
  "inferred_fields": {},
  "mapped_fields": {},
  "mapping_metadata": {},
  "ai_review": {},
  "validation": {
    "missing_fields": [],
    "thin_content": [],
    "warnings": []
  },
  "needs_manual_review": false
}
```

## Core approach: Dual-Engine Supervised Pipeline

The system uses a sophisticated three-stage "Supervised Hybrid" architecture to ensure maximum accuracy and zero missing data.

### Engine 1: Deterministic + AI Review (Baseline)
This engine handles the structured and factual work:
- **Deterministic:** Extracts tables, stats, and headings using Regex and structural rules.
- **AI Review:** Uses Groq to fill ambiguous scalar fields and generate sensible marketing copy for UI elements (CTAs, button texts, form headings).

### Engine 2: Semantic AI (Contextual Retrieval)
This engine uses Vector Embeddings to understand the document's nuances:
- **Embeddings:** Uses `all-MiniLM-L6-v2` (Sentence Transformers) to convert document chunks into vectors.
- **Vector Store:** Stores chunks in **ChromaDB** during the upload lifecycle.
- **Retrieval:** Performs **Cosine Similarity Search** for every ACF section to find the most relevant context.
- **Extraction:** Uses Groq to extract values based purely on the retrieved semantic context.

### Engine 3: Supervisor AI (Decision Logic)
This is the final judge that merges the two engines:
- **Comparison:** Compares the output of Engine 1 and Engine 2 field-by-field.
- **Decision:** If values differ, the Supervisor evaluates which engine provided a more accurate or better-formatted response.
- **Output:** Returns the final, polished JSON payload ready for WordPress.

This approach combines the strict accuracy of deterministic rules with the flexible reasoning of semantic search.


## Project structure

```text
degreebaba_ai/
├── frontend/
├── backend/
├── sample_docs/
├── requirements.txt
└── README.md
```

### Frontend

The frontend is intentionally simple.

It provides:

- file upload
- final JSON output
- validation report
- status / flags like confidence, AI review status, and manual review requirement

### Backend

The backend is a FastAPI service that contains the parsing and mapping pipeline.

## Backend folders

```text
backend/
├── main.py
├── .env
├── .env.example
├── ai/
├── classifier/
├── html_templates/
├── mapper/
├── parser/
├── prompts/
├── schemas/
├── utils/
└── validators/
```

## How the pipeline works

### 1. DOCX reading

The backend reads:

- paragraphs
- paragraph styles
- tables
- raw text

This gives us both structure and full-text fallback.

### 2. Section grouping

The system groups content under headings so later stages can work with semantic sections like:

- About
- Eligibility
- Fee Structure
- Admission Process
- FAQs

### 3. Page classification

The classifier looks at:

- heading patterns
- section names
- page intent
- template similarity

Then it selects exactly one page type:

- `university`
- `course`
- `specialization`

### 4. Schema and template understanding

The HTML templates are treated as source of truth for page structure.

The schema layer:

- loads the nested schema JSON
- flattens it into mapper-safe field paths
- later rebuilds the final nested payload

### 5. Page-specific mapping

Instead of using one generic mapper for everything, the backend uses dedicated mappers:

- `university_mapper.py`
- `course_mapper.py`
- `specialization_mapper.py`

This is what makes the extraction more stable.

### 6. AI review

After deterministic mapping:

- weak text fields are reviewed by AI
- missing hero stats can be reviewed by AI
- AI changes are verified before acceptance

If AI is unavailable, the output is flagged for manual review.

### 7. Validation

The validator checks:

- missing fields
- thin content
- malformed repeater shapes
- duplicate stats
- AI review warnings

## Frontend flow

The current frontend is intentionally minimal.

### Upload

User uploads a DOCX file.

### JSON

Frontend shows the final JSON payload that can later be sent to WordPress.

### Validation

Frontend shows:

- missing fields
- thin content
- warnings

The status card also shows:

- page type
- confidence
- AI review status
- whether manual review is required

## Environment setup

Backend env file:

[backend/.env](/Users/arhanalam/Desktop/degreebaba_ai/backend/.env)

Example:

```env
GROQ_ENABLED=true
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
GROQ_BASE_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_TIMEOUT_SECONDS=25
```

Reference:

[backend/.env.example](/Users/arhanalam/Desktop/degreebaba_ai/backend/.env.example)

## Run locally

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API

### Health check

`GET /health`

### Parse document

`POST /parse`

Multipart field:

- `file`

Accepted file type:

- `.docx`

## Current product behavior

### What it already does well

- page classification
- nested schema output
- page-specific deterministic mapping
- final JSON generation
- validation reporting
- AI review stage wiring

### What is intentionally not implemented yet

- WordPress post creation/update
- duplicate-post prevention logic in WordPress
- draft reset after re-upload

Those are planned for the next phase.

## Safety decisions

This project is designed to prefer safe output over fake output.

That means:

- if content is missing, return `null` or `[]`
- do not invent stats
- do not invent fee rows
- do not invent faculty/recruiters/banks
- raise warnings instead of hiding uncertainty

## Files worth opening first

If you are new to the codebase, start here:

- [backend/main.py](/Users/arhanalam/Desktop/degreebaba_ai/backend/main.py)
- [backend/parser/docx_reader.py](/Users/arhanalam/Desktop/degreebaba_ai/backend/parser/docx_reader.py)
- [backend/parser/section_parser.py](/Users/arhanalam/Desktop/degreebaba_ai/backend/parser/section_parser.py)
- [backend/classifier/page_classifier.py](/Users/arhanalam/Desktop/degreebaba_ai/backend/classifier/page_classifier.py)
- [backend/mapper/field_mapper.py](/Users/arhanalam/Desktop/degreebaba_ai/backend/mapper/field_mapper.py)
- [backend/mapper/university_mapper.py](/Users/arhanalam/Desktop/degreebaba_ai/backend/mapper/university_mapper.py)
- [backend/mapper/course_mapper.py](/Users/arhanalam/Desktop/degreebaba_ai/backend/mapper/course_mapper.py)
- [backend/mapper/specialization_mapper.py](/Users/arhanalam/Desktop/degreebaba_ai/backend/mapper/specialization_mapper.py)
- [backend/ai/hybrid_mapper.py](/Users/arhanalam/Desktop/degreebaba_ai/backend/ai/hybrid_mapper.py)
- [backend/validators/validator.py](/Users/arhanalam/Desktop/degreebaba_ai/backend/validators/validator.py)
- [frontend/src/pages/ParserPage.jsx](/Users/arhanalam/Desktop/degreebaba_ai/frontend/src/pages/ParserPage.jsx)

## Interview prep

I also created a separate file for interview explanation:

[INTERVIEW_GUIDE.md](/Users/arhanalam/Desktop/degreebaba_ai/INTERVIEW_GUIDE.md)

That document explains:

- what each important file does
- how data flows end to end
- how to explain the deterministic + AI hybrid approach
- what tradeoffs were made
