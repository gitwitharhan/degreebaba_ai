# Strategic Engineering Roadmap: 2-Week Development Plan

**Author:** Arhan Alam (AI Research & Development Intern)
**Context:** Future Expansion Vision for the DegreeBaba Document Parsing Pipeline

If granted two additional weeks of dedicated research and development, I would prioritize the following architectural enhancements to transition this micro-app into an enterprise-grade ingestion system:

## 1. Advanced Semantic-Aware Chunking (Days 1–3)
Currently, the vector search engine splits DOCX files using fixed-character chunking (500 chars, 100 overlap). While fast, this occasionally shears sentences or tabular contexts in half, resulting in minor vector search noise. I would implement a **Semantic Chunking Parser** that honors the document's physical and syntax structural elements (e.g., separating by headings, paragraphs, and list blocks). This guarantees that every vector chunk contains a clean, logically whole context.

## 2. Multi-Modal Media Extraction Pipeline (Days 4–6)
Word documents authored by content writers often contain critical images, high-resolution logos, and placement infographics. The current text-only pipeline ignores these files. I would build a parser using `python-docx` zip stream access to isolate embedded image bytes during ingestion, push them to a temporary S3 bucket (or local media cache), auto-run OCR (Tesseract or Vision LLM) to capture content, and automatically insert the asset URL strings inside the final ACF image subfields.

## 3. Direct WordPress REST API Native Sync (Days 7–9)
To bridge the gap to production, the validated JSON payload should automatically populate WordPress drafts. I would develop a secure REST API synchronization client. Once the validation report passes without blocking warnings, the client will connect directly to the target WordPress instance, check page existence, compile the ACF repeater structures into WP's flat metadata tables, and draft the pages. This will eliminate manual copy-pasting entirely, reducing final publication overhead to zero.

## 4. Batch Quality Regression Testing (Days 10–12)
As schemas evolve, mapping rules must remain stable. I would establish a regression test suite running parallel evaluations on a golden dataset of 100+ documents. The system will calculate token efficiencies and field-level cosine distance metrics, reporting mapping performance over time and guarding against LLM degradation or prompt drift.

## 5. Deployment Containerization & Monitoring (Days 13–14)
I would wrap the FastAPI application in a multi-stage Docker container optimized for CPU tasks (pre-downloading the sentence-transformers model files during build) and incorporate standard telemetry monitoring (e.g., Prometheus metrics tracking API latency, token consumption, and database ephemeral collections). This will guarantee scalable and stable execution in high-concurrency staging environments.
