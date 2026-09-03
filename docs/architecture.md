# Architecture

## System overview

```text
React Frontend (Vite + Tailwind)
        │  REST / JSON, Axios
        ▼
FastAPI Backend
        │
        ├── Document Processing
        │       Upload → Validate → Store → Extract (PyMuPDF)
        │       → Clean → Chunk (page-aware, word-window)
        │
        ├── Embeddings (local ONNX MiniLM, all-MiniLM-L6-v2)
        │       Runs offline after a one-time model download.
        │       No API key required.
        │
        ├── ChromaDB (persistent, cosine similarity)
        │       One collection ("chunks"), embeddings computed
        │       externally and passed in explicitly.
        │
        ├── Retrieval
        │       question → query embedding → vector search (Top-K)
        │       → similarity threshold filter → optional document scoping
        │
        ├── Reranking (disabled by default)
        │       Pass-through hook; a real cross-encoder can be dropped
        │       in later without touching chat_service.
        │
        ├── Context Builder
        │       Retrieved chunks → numbered SOURCE blocks, size-bounded
        │       by MAX_CONTEXT_CHARS.
        │
        ├── LLM (Anthropic Claude, via the official SDK)
        │       Grounded system prompt + context + limited conversation
        │       history → answer.
        │
        └── Citations
                Built directly from retrieved chunks before the LLM call -
                the LLM never supplies citation metadata.
```

## Layered backend design

```text
API (routes)        - thin, no business logic
   ↓
Services            - orchestration, one responsibility each
   ↓
RAG (rag/)          - chunking, context building, prompt, citations
   ↓
DB (repositories)   - all SQL in one place
   ↓
Utils               - file/text helpers, no framework dependencies
```

Routes call services; services call repositories/RAG modules; nothing skips
a layer. This is what let Phase 2 (embeddings/retrieval/chat) and Phase 3
(frontend) be added without rewriting Phase 1 code.

## Document lifecycle

```text
uploaded → processing → indexed
                     ↘ failed (validation error, extraction error,
                                embedding/vector-store error)
```

A document only reaches `indexed` after its chunks are embedded and
successfully written to ChromaDB. If any step in the pipeline fails after
the record was created, partial vectors for that document are deleted
before the status flips to `failed` - a failed document never leaves stray
vectors behind. Deleting a document removes its SQLite row, its stored PDF,
and its ChromaDB vectors together.

## Chat flow

```text
POST /api/chat {question, document_ids?, conversation_id?}
        │
        ▼
Validate question (non-empty, within MAX_QUESTION_LENGTH)
        │
        ▼
Resolve/create conversation, load limited history (CONVERSATION_HISTORY_LIMIT)
        │
        ▼
Retrieve: embed question → ChromaDB search, scoped to indexed documents
          (and further to document_ids, if given) → similarity threshold
        │
        ▼
Rerank (no-op unless RERANKER_ENABLED)
        │
        ├── No evidence above threshold ──► fixed no-evidence response
        │                                    (LLM never called)
        │
        ▼
Build citations from retrieved chunks → build bounded context
        │
        ▼
Call LLM with grounded system prompt + context + history
        │
        ▼
Persist user + assistant messages → return {answer, grounded, sources}
```

## No-evidence protection

This is enforced in code, not by prompting alone: `chat_service.answer`
only calls the LLM when retrieval returns at least one chunk above
`SIMILARITY_THRESHOLD`. When it doesn't, the fixed response
(`grounded: false`, `sources: []`, a fixed message) is returned directly -
the LLM is structurally unreachable for that request, so it cannot
hallucinate an answer from outside the uploaded documents.

## Vector storage

Each chunk is stored in ChromaDB with a deterministic id
(`{document_id}_page_{n}_chunk_{n}`), its text, and metadata
(`document_id`, `filename`, `page`). Upserts are idempotent - reprocessing
the same document never creates duplicate vectors. The collection uses
cosine space; a match's score is `1 - cosine_distance`.

## Conversation flow

The backend persists `conversations` and `messages` (SQLite), and
`POST /api/chat` is the only conversation-facing endpoint - there is no
list/read endpoint for prior conversations. The frontend's Conversations/
History screen is built by mirroring each real chat exchange into
`localStorage` as it happens, rather than inventing a backend endpoint.

## Frontend

React function components, React Router for navigation, a single Axios
instance (`src/api/client.js`) as the only place that talks to the backend,
and three hooks (`useHealth`, `useDocuments`, `useChat`) that own all
server-state fetching. Nothing in the frontend fabricates data: every
number, status, and citation shown comes from a real backend response.
