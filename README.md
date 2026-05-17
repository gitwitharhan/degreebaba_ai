# DegreeBaba — AI Content Parsing Micro App

A sophisticated document parsing pipeline designed to bridge the gap between creative content writers (Word documents) and WordPress Advanced Custom Fields (ACF).

Developed for **DegreeBaba AI Intern Task (May 2026)**.

---

## 📄 System Research Paper (PDF Generated)
A comprehensive, academic-grade research paper detailing the system's technical design, empirical findings, and operational impact has been programmatically generated in the project root:
- **Research Paper PDF:** [DegreeBaba_Research_Paper.pdf](file:///Users/arhanalam/Desktop/degreebaba_ai/DegreeBaba_Research_Paper.pdf)
- **PDF Generator Script:** [generate_research_pdf.py](file:///Users/arhanalam/Desktop/degreebaba_ai/generate_research_pdf.py) (Run via `python3 generate_research_pdf.py` to compile a fresh copy).

---

## 🚀 Architectural Vision & Core Value Proposition
This micro-app automates the ingestion of unstructured, narrative-heavy DOCX files and maps them to highly strict, structured, and type-safe JSON payloads for **University**, **Course**, and **Specialization** pages.

Instead of relying on unstable end-to-end LLM prompts, this pipeline employs a **Supervised Dual-Engine Hybrid Architecture**:
1. **Engine 1 (Deterministic Baseline):** Regex and rule-based parsing for structured grids, fees, syllabus matrices, and exact numbers.
2. **Engine 2 (Semantic AI RAG-Lite):** Local sentence-transformer embeddings (`all-MiniLM-L6-v2`) and in-memory ChromaDB vector search to map fluid narrative contexts.
3. **Engine 3 (Supervisor AI):** An intelligent judge that merges the two engine outputs, resolves conflicts, and synthesizes missing UI metadata (e.g. CTA buttons, lead forms).
4. **Deep Nested Validation:** Enforces schema integrity, counts words for SEO thin-content checks, validates statistical boundaries, and guarantees web-safe payloads before publication.

---

## 🛠 Tech Stack
*   **Backend:** FastAPI (Python 3), Uvicorn, ChromaDB (Ephemeral Client), Sentence-Transformers, Groq API (Qwen-32b model).
*   **Frontend:** React, Vite, Vanilla CSS (Modern aesthetic, glassmorphism, fully responsive).

---

## 🏃‍♂️ Quick Start (Local Setup)

### 1. Backend Setup
1. Open a terminal and navigate to the backend workspace directory.
2. Install the necessary Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the `backend/` folder and add your Groq API key:
   ```env
   GROQ_API_KEY=gsk_your_actual_key_here
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn backend.main:app --reload
   ```
   *The backend will run on `http://127.0.0.1:8000`.*

### 2. Frontend Setup
1. Open a second terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install the package dependencies:
   ```bash
   npm install
   ```
3. Launch the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend will run on `http://127.0.0.1:5173`.*

---

## 🧠 Comprehensive Architectural Deep-Dive

### Engine 1: The Deterministic Structural Baseline
*   **Technology:** Python, regex patterns, native `python-docx` XML reader.
*   **Target Fields:** Academic Syllabus grids, Course Fees, Eligibility tables, FAQs.
*   **Rationale:** LLMs struggle with verbatim copying of large data matrices and numbers, and are prone to text modifications. Engine 1 parses XML table nodes directly, guaranteeing 100% mathematical and transcription accuracy.

### Engine 2: The Semantic Vector RAG-Lite Engine
*   **Technology:** ChromaDB (Ephemeral, in-memory collection per session), Sentence-Transformers `all-MiniLM-L6-v2` (384-dimension embeddings), Groq Qwen-32B API.
*   **Target Fields:** Hero badges, placement summaries, creative overviews, marketing highlights.
*   **Rationale:** Authors write descriptions using unique headlines and synonyms. To match these to our strict ACF labels without blowing the LLM's context window, we chunk the text (500 chars, 100 overlap), index them, and query the vector store field-by-field. The LLM only processes the top 3 highly relevant paragraphs, eliminating noise and hallucinations.

### Engine 3: The Multi-Agent Supervisor Engine
*   **Technology:** Groq Qwen-32B.
*   **Rationale:** The Supervisor compares Engine 1 and Engine 2 outputs field-by-field:
    *   If one is empty, the populated value is chosen.
    *   If they conflict, numbers/grids default to Engine 1, whereas paragraphs/marketing copy default to Engine 2.
    *   **UI Synthesis:** If crucial web elements (like CTA button text, dynamic sidebar lead form titles) are missing from the draft, the Supervisor synthesizes professional, high-converting contextual copy (e.g. converting a course name to `"Enquire about B.Tech in CS Now!"`), preventing empty fields on front-end layouts.

### 4. Deep Nested Validation Layer
*   **Deep Array Checks:** Recursively parses inside repeater blocks (like FAQ items) to confirm that no subfield (like the question or answer text) is blank.
*   **SEO Protection:** WYSIWYG rich text fields are assessed for length; values below 20 words trigger a `thin_content` warning.
*   **UI Safety:** numerical stats are scrutinized for duplicate entries and verified to ensure they do not exceed 6 characters, safeguarding visual grids on small mobile screens.
*   **Safe Nulls:** The system prefers adding a clean warning to the `needs_manual_review` dashboard over fabricating mock data for strict legal/academic fields, keeping publication control firmly with the platform administrator.

---

## 📁 Repository Structure
```text
├── README.md                      # Main project guide (Standard Markdown)
├── DegreeBaba_Research_Paper.pdf  # Technical Research Paper (Generated PDF)
├── generate_research_pdf.py       # Python script to compile the PDF
├── INTERVIEW_GUIDE.md             # High-level technical interview study sheet
├── requirements.txt               # Main python packages
├── backend/                       # FastAPI Server
│   ├── main.py                    # Orchestration entry point
│   ├── ai/                        # ChromaDB, RAG, and Supervisor modules
│   ├── classifier/                # Page layout classification models
│   ├── mapper/                    # Regex, deterministic rules & helpers
│   ├── schemas/                   # Canonical ACF schema documents
│   └── validators/                # Deep nested validation logic
└── frontend/                      # React SPA
    ├── src/                       # Components, Pages & CSS Styling
    └── package.json               # Frontend dependencies
```

---

*Developed by Arhan Alam — AI Research & Development Team.*
