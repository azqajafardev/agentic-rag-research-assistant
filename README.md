# EvidenceRAG

**Evidence-based AI research assistant.** Upload research papers, ask questions, and get answers grounded in your documents - with page-level citations you can inspect, and an honest "I don't know" when the evidence isn't there.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector%20store-6C3EF4)
![Tests](https://img.shields.io/badge/tests-35%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

`retrieval-augmented-generation` · `agentic-ai` · `generative-ai` · `llm` · `fastapi` · `chromadb` · `python` · `react` · `ai-research-assistant` · `semantic-search` · `machine-learning`

## Overview

EvidenceRAG is a full-stack Retrieval-Augmented Generation (RAG) application: FastAPI backend, ChromaDB vector store, local embeddings, Claude for grounded generation, and a React + Tailwind frontend. It's built to demonstrate real RAG engineering - not just an LLM API call wrapped in a chat box - with hallucination-resistant design as a first-class requirement, not an afterthought.

Read [docs/rag-explained.md](docs/rag-explained.md) for a plain-language walkthrough of the pipeline and the reasoning behind the key design decisions (why RAG, why ChromaDB, why page-aware chunks, how hallucination is reduced).

## Features

- Multi-PDF upload with real-time processing status (uploaded → processing → indexed/failed)
- Page-aware chunking that preserves document/page metadata all the way to the final citation
- Local embeddings (no API key required) via ChromaDB's bundled ONNX MiniLM model
- Semantic retrieval with a configurable similarity threshold and per-document scoping
- **Structural no-evidence protection**: the LLM is never called when retrieval finds nothing above threshold - not a prompting convention, an actual code path
- Citations built from real retrieved chunks before the LLM ever runs - the LLM cannot fabricate a citation
- Conversation history with limited context passed to the LLM (never unbounded)
- A professional, portfolio-quality React interface: dashboard, document management, chat workspace, evidence panel, conversation history
- A lightweight, honest evaluation harness (real scores only - see [Evaluation](#evaluation))
- Dockerized for one-command startup

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full breakdown (document lifecycle, chat flow, no-evidence protection, vector storage, conversation flow).

```text
React (Vite + Tailwind) → FastAPI → Document Processing → Chunking
  → Embeddings (local ONNX MiniLM) → ChromaDB → Retrieval → Reranking (off)
  → Context Builder → Claude (Anthropic) → Citations → back to React
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS v4, React Router, Axios, lucide-react |
| Backend | Python 3.13, FastAPI, Uvicorn, Pydantic |
| Document processing | PyMuPDF |
| Embeddings | ChromaDB's local ONNX MiniLM (`all-MiniLM-L6-v2`) - no API key |
| Vector store | ChromaDB (persistent, cosine similarity) |
| LLM | Anthropic Claude (official `anthropic` SDK) |
| App database | SQLite |
| Testing | pytest, FastAPI `TestClient` |
| Deployment | Docker, Docker Compose |

## RAG Pipeline

```text
Upload → Validate → Store → Extract (PyMuPDF, page-by-page)
  → Clean text → Chunk (page-aware, ~800 words, 120 overlap)
  → Embed (local MiniLM) → Index (ChromaDB, deterministic chunk ids)

Question → Embed → Vector search (Top-K) → Similarity threshold
  → [below threshold: fixed no-evidence response, LLM never called]
  → Rerank (pass-through by default) → Build citations from real chunks
  → Build bounded context → Grounded LLM call → Persist → Respond
```

## Screenshots

Not yet captured in this checkout - see [screenshots/README.md](screenshots/README.md)
for the exact list of screens to capture and where to drop them before
publishing (Dashboard, Documents, Upload, New Chat, Grounded Answer,
Sources, No-Evidence, Conversation History).

## Demo

A concrete walkthrough to run live (or narrate from screenshots) in an interview:

1. Upload a research PDF and watch its status move `uploaded → processing → indexed`
2. Open **New Chat**, scope it to the uploaded paper
3. Ask a question the paper actually answers - get a grounded answer
4. Open the evidence panel - inspect the page-level citations behind that answer
5. Ask a follow-up question in the same conversation - it uses the prior turns as context
6. Ask something the paper doesn't cover - see the no-evidence response (`grounded: false`, no sources, no LLM call made)
7. Check **Conversation History** - both exchanges are there
8. Delete the document - its vectors are removed from ChromaDB along with its record

## Installation

Requires Python 3.12+ and Node.js 20+.

```bash
git clone <this-repo>
cd agentic-rag-research-assistant
```

## Environment Setup

**Backend** (`backend/.env`, copy from `backend/.env.example`):

```env
LLM_PROVIDER=groq                    # or anthropic
LLM_MODEL=openai/gpt-oss-20b         # or claude-opus-5 for anthropic
LLM_API_KEY=your-provider-api-key    # required for grounded answers
FRONTEND_URL=http://localhost:5173
```

Everything else has a sensible default (see `backend/.env.example` for the full list: `TOP_K`, `SIMILARITY_THRESHOLD`, `MAX_UPLOAD_SIZE_MB`, etc.). No key is required for embeddings, uploads, retrieval, or the no-evidence path - only `/api/chat`'s grounded-answer path needs `LLM_API_KEY`.

### LLM provider

Two providers are supported, selected by `LLM_PROVIDER` - the rest of the app (retrieval, citations, context building, chat) is identical either way, since both sit behind the same `LLMService.generate()` interface:

- **`groq`** (recommended for development) - free tier, no cost. Get a key at [console.groq.com/keys](https://console.groq.com/keys). Uses Groq's OpenAI-compatible REST API directly over `httpx` - no extra dependency.
- **`anthropic`** (used in production) - paid, via the official `anthropic` SDK.

`LLM_API_KEY` always comes from `.env` (or the shell environment) - it is never hardcoded and `backend/.env` is git-ignored. Never commit a real key to `backend/.env.example` or anywhere else in the repo.

**Frontend** (`frontend/.env`, copy from `frontend/.env.example`):

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

## Local Run Instructions

**Backend**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend: http://127.0.0.1:8000 · Swagger: http://127.0.0.1:8000/docs

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
Frontend: http://localhost:5173

## Docker Run Instructions

```bash
cp .env.example .env      # fill in LLM_API_KEY
docker compose up --build
```
Backend: http://localhost:8000 · Frontend: http://localhost:5173. Document metadata, uploaded PDFs, and ChromaDB data persist in the `backend_data` named volume across restarts.

> The Docker configuration was written and reviewed carefully but could not be run in the environment this project was built in (no Docker available there) - verify with `docker compose up --build` before relying on it, and see the project's implementation notes for what was and wasn't live-tested.

## Testing

```bash
cd backend
pytest -v
```
35 tests covering document validation, page-aware chunking, retrieval/threshold/citation behavior, no-evidence protection, conversation handling, and the full API surface. External embedding/LLM calls are mocked with deterministic fakes - no paid API access or internet required to run the suite.

## Evaluation

```bash
backend\.venv\Scripts\python.exe evaluation\run_evaluation.py    # Windows
backend/.venv/bin/python evaluation/run_evaluation.py            # macOS/Linux
```

Self-contained (builds its own isolated document store, no server needed). Measures retrieval relevance, citation correctness, groundedness, and no-evidence behavior against a fixed 8-question dataset - see [evaluation/README.md](evaluation/README.md) for details and exactly what is/isn't measured without an `LLM_API_KEY` configured.

## API Documentation

See [docs/api.md](docs/api.md) for every endpoint, request/response shape, and error code. Live interactive docs at `/docs` while the backend is running.

## Security

- No secrets in source: `LLM_API_KEY` and all other config come from `.env` files, which are git-ignored (`backend/.env`, `frontend/.env`); only `.env.example` templates are committed.
- Runtime data (`backend/data/uploads/*`, SQLite DB, ChromaDB directory) is git-ignored - only the app code and empty directory placeholders are tracked.
- File upload validation: content-type/extension check, empty-file rejection, size cap (`MAX_UPLOAD_SIZE_MB`), and a real PDF-parse check (not just the extension) before a file is trusted.
- Question length is capped (`MAX_QUESTION_LENGTH`) and conversation history sent to the LLM is bounded (`CONVERSATION_HISTORY_LIMIT`) - no unbounded input reaches the model.
- CORS is restricted to a single configured origin (`FRONTEND_URL`), not `*`.
- Errors return a stable `{error: {code, message}}` shape; internal exception details and stack traces are never leaked to the client (see [docs/api.md](docs/api.md) for the full error-code table).
- The Docker image runs the backend as a non-root user.

## Limitations

Said plainly, so nothing here is oversold:

- Reranking is implemented as a pass-through hook (`RerankerService`) but not wired to a real cross-encoder model - it exists so one can be dropped in without touching `chat_service`.
- Conversation history is client-side (`localStorage`) rather than backend-queryable, because no conversation-list endpoint exists yet - documented in [docs/architecture.md](docs/architecture.md#conversation-flow).
- Chunking is a fixed word-window, not semantic/section-aware - a chunk boundary can still fall mid-sentence within a page.
- Single-user by design - no auth, no multi-tenancy.
- Chat responses are not streamed - the full answer returns in one response.
- The Docker setup was written and reviewed but not live-verified in the environment this project was built in (no Docker there) - verify with `docker compose up --build` before relying on it in production.

## Future Improvements

- Cross-encoder reranking (the `RerankerService` hook already exists; disabled by default)
- Semantic/section-aware chunking beyond the current word-window approach
- Hybrid BM25 + vector search
- A backend endpoint for listing/reading past conversations (currently client-side only, since none exists yet)
- Streaming chat responses
- Multi-user auth and workspaces

## License

MIT
