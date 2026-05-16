# Interview Guide: DegreeBaba DOCX to ACF Parser

This document is the ultimate reference for explaining the project during an interview. It covers architecture, technical decisions, and common "why" questions.

---

## 1. The Core Value Proposition
**"How do you describe this project in one minute?"**
> "I built a Dual-Engine AI pipeline that converts natural language Word documents into structured ACF (Advanced Custom Fields) JSON for WordPress. It uses a **Supervised Hybrid** approach: a deterministic engine for structural accuracy (tables/stats) and a semantic engine (Vector Store + LLM) for narrative context. A third 'Supervisor' AI merges both to ensure the final payload is accurate and production-ready."

---

## 2. Technical Architecture: The Three Engines

### Engine 1: Deterministic Baseline
- **Technology:** Python, Regex, `python-docx`.
- **Role:** Handles high-confidence structural data like tables, FAQs, and stats.
- **Why?** LLMs often struggle with large tables or exact numbers. Deterministic rules ensure 100% accuracy for factual data.

### Engine 2: Semantic AI (RAG-Lite)
- **Technology:** ChromaDB (Vector Store), `all-MiniLM-L6-v2` (Embeddings), Groq/Qwen-32b.
- **Role:** Document is chunked and indexed. For every ACF field, we perform a **Cosine Similarity Search** to find relevant context.
- **Why?** This handles "messy" documents where headings don't match our schema. It understands synonyms and context.

### Engine 3: Supervisor AI (The Judge)
- **Technology:** Groq/Qwen-32b.
- **Role:** Compares results from Engine 1 and Engine 2 field-by-field.
- **Special Power:** **Synthesis.** If both engines return `null` for a UI field (like a CTA button), the Supervisor synthesizes a context-aware value so the UI doesn't look empty.

---

## 3. Key Files & Responsibilities

### Core Orchestration
- **[backend/main.py](file:///Users/arhanalam/Desktop/degreebaba_ai/backend/main.py):** The entry point. It orchestrates the flow: Parse -> Classify -> Engine 1 -> Engine 2 -> Engine 3 -> Validate.
- **[backend/classifier/page_classifier.py](file:///Users/arhanalam/Desktop/degreebaba_ai/backend/classifier/page_classifier.py):** Predicts if the doc is a University, Course, or Specialization. High confidence triggers specific mapping rules.

### Mapping & Logic
- **[backend/mapper/university_mapper.py](file:///Users/arhanalam/Desktop/degreebaba_ai/backend/mapper/university_mapper.py):** Page-specific deterministic rules. (Same for Course/Specialization).
- **[backend/mapper/content_utils.py](file:///Users/arhanalam/Desktop/degreebaba_ai/backend/mapper/content_utils.py):** Shared "battle-tested" helpers for extracting FAQs, Stats, and Steps.

### AI & Vector Store
- **[backend/ai/vector_store.py](file:///Users/arhanalam/Desktop/degreebaba_ai/backend/ai/vector_store.py):** Manages the ephemeral ChromaDB collection for the document session.
- **[backend/ai/supervisor.py](file:///Users/arhanalam/Desktop/degreebaba_ai/backend/ai/supervisor.py):** Contains the decision-making logic and the synthesis prompt.

### Validation
- **[backend/validators/validator.py](file:///Users/arhanalam/Desktop/degreebaba_ai/backend/validators/validator.py):** Performs "Deep Validation." It checks for nulls even inside repeaters to prevent broken layouts in WordPress.

---

## 4. Tough Interview Questions (The "Cheat Sheet")

### "Why use a Vector Store (ChromaDB) for a single document?"
> "It allows for **Semantic Retrieval** per field. Instead of passing the whole document to the LLM (which is expensive and noisy), we only pass the most relevant chunks for a specific ACF field. This increases accuracy and reduces hallucinations."

### "How do you handle data loss or fake data?"
> "We prefer 'Safe Nulls' over 'Fake Data.' If both engines fail and the field isn't a UI field, we return `null` and flag it in the **Validation Report**. This transparency is better than a broken or incorrect production page."

### "What was the hardest challenge?"
> "FAQ and Table extraction from Word. Word documents have inconsistent formatting. I solved this by building a robust `content_utils` library that uses Regex lookaheads and keyword patterns to separate questions from answers correctly."

### "Why page-specific mappers instead of one big AI prompt?"
> "Reliability. WordPress ACF schemas are strict. Page-specific mappers allow us to use deterministic logic where it works best (e.g., Syllabus tables) while using AI only where it's needed (e.g., Marketing copy)."

---

## 5. What's Next? (Future Roadmap)
1. **Direct WordPress Integration:** Using the WP-JSON API to push the verified payload.
2. **Batch Evaluation:** Running 100+ documents through a testing script to measure field-level accuracy.
3. **Image Extraction:** Handling images/logos inside the DOCX using `python-docx` image blobs.

---

## 6. Closing Statement
> "This project isn't just a parser; it's a **Production Content Pipeline**. It solves the real-world gap between creative writers (Word) and technical developers (ACF/WordPress) using a supervised AI architecture."
