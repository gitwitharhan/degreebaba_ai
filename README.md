# DegreeBaba — AI Content Parsing Micro App

A sophisticated document parsing pipeline designed to bridge the gap between content writers (Word documents) and WordPress ACF (Advanced Custom Fields).

## 🚀 Overview
This micro-app automates the mapping of narrative DOCX files to structured JSON payloads for University, Course, and Specialization pages on the DegreeBaba platform.

### Key Features
- **Dual-Engine Mapping:** Combines a deterministic engine (Regex/Rules) with a semantic engine (Vector Store + LLM).
- **Intelligent Supervision:** A Supervisor AI compares engine outputs and synthesizes missing UI/marketing data.
- **Deep Validation:** Automatically detects missing fields, thin content, and malformed data even inside nested repeaters.
- **Vector Search:** Uses ChromaDB and `all-MiniLM-L6-v2` embeddings to retrieve field-specific context from documents.

## 🛠 Tech Stack
- **Backend:** FastAPI, Python, ChromaDB, Sentence-Transformers, Groq (Qwen-32b).
- **Frontend:** React, Vite, Vanilla CSS.

## 🏃‍♂️ Quick Start (Local)

### 1. Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file in /backend
# Add GROQ_API_KEY=your_key_here

# Start the server
uvicorn backend.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure
- `backend/`: FastAPI server and AI logic.
  - `ai/`: Vector store, hybrid mapping, and supervisor logic.
  - `mapper/`: Page-specific mapping rules.
  - `schemas/`: Canonical ACF field definitions.
- `frontend/`: React application.
- `sample_docs/`: Sample DOCX files for testing.
- `INTERVIEW_GUIDE.md`: Comprehensive guide for technical discussions.

## 🧠 Architecture
For a deep dive into the system design, conflict resolution, and AI verification steps, please refer to the [INTERVIEW_GUIDE.md](./INTERVIEW_GUIDE.md).

---
*Developed for DegreeBaba AI Intern Task (May 2026).*
