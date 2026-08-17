# CampusAI — University AI Assistant

CampusAI is a production-style, single-agent university assistant that combines advanced prompt engineering, grounded Retrieval-Augmented Generation (RAG) over an official university handbook, Groq tool calling for controlled campus actions, local vector search using Qdrant, local embeddings, session-level memory, explicit safety confirmation for higher-risk actions, and lightweight LLMOps.

---

## 🛠️ Architecture

```
         [ React + Vite Frontend ]
                     │
                     ▼
             [ FastAPI Backend ]
                     │
                     ▼
        [ Single Groq Agent (70B) ]
         ├── RAG (Qdrant Local Vector DB)
         └── Deterministic Python Tools
```

- **Frontend**: Built using React, Vite, and Vanilla CSS. Implements glassmorphism dark aesthetics with active page simulation, handbook download handlers, and contact confirmation dialogs.
- **FastAPI Backend**: Serves API routes, runs input validations/guardrails, manages session store, and performs error containment.
- **Single Groq Agent**: Uses `llama-3.3-70b-versatile` for tool-selection, parameter parsing, and grounded policy answers.
- **RAG & Search**: Powered by local embeddings (`BAAI/bge-small-en-v1.5` using `sentence-transformers`) and a local vector search engine (`Qdrant` Local).
- **Session Memory**: In-memory Python dictionaries storing up to 12 conversational turns per session.

---

## 🚦 Decision Gate & Design Justifications

- **Prompting**: **YES**. Established CampusAI identity, grounding, strict tool calling scopes, input/output validation, and prompt injection protection.
- **RAG**: **YES** (University Handbook Only). Ensures answers about regulations (attendance, grading, admissions) are completely grounded in the official handbook, eliminating hallucinated policies.
- **Agentic AI**: **YES** (Single Agent). The agent handles tool-selection, reasoning, and grounding in a single execution step, avoiding complex multi-agent overhead.
- **MCP**: **NO**. As the app features a small set of fixed, tightly coupled local tools, a direct python function execution approach is simpler and more maintainable.
- **Fine-Tuning**: **NO**. Grounded RAG with system instruction constraints is highly effective and cheaper than training custom parameters.
- **Distillation**: **NO**. No student/teacher training was implemented to keep the architecture clean and simple.
- **LLMOps**: **YES** (Lightweight). Leverages Python's standard logging module to log latency (request, RAG, tool execution), similarity search scores, selected tools, and error boundaries, while strictly avoiding logging PII.

---

## 🚀 Setup & Execution

### 1. Prerequisites & Environment Setup

Clone/navigate to the project and initialize a Python virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory (based on `.env.example`):

```bash
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
QDRANT_PATH=./qdrant_data
HANDBOOK_PATH=./data/university_handbook.pdf
TOP_K=3
```

### 3. Generate Mock Handbook & Ingest Vectors

If you do not have the handbook PDF, generate our pre-structured handbook mock first:

```bash
python scripts/generate_mock_pdf.py
```

Run vector database ingestion script to parse, chunk, embed, and index handbook data into local Qdrant collection:

```bash
python scripts/ingest.py
```

### 4. Run Backend Server

Launch the FastAPI application:

```bash
uvicorn backend.main:app --reload --port 8000
```

Verify backend health at: [http://localhost:8000/health](http://localhost:8000/health).

### 5. Run Frontend Client

Open a new terminal, navigate to the `frontend` folder, and configure its `.env` file:

```bash
cd frontend
# Create .env file based on example
copy .env.example .env
```

Install packages and boot the Vite server:

```bash
npm install
npm run dev
```

Visit the frontend client at: [http://localhost:5173](http://localhost:5173).
