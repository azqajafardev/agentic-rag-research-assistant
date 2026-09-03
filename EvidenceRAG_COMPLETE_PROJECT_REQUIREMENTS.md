# EvidenceRAG — Complete AI Research Assistant
## Full Project Requirements, Architecture, UI, Backend, RAG, Testing & Deployment

**Project Type:** AI / Generative AI / RAG / Full-Stack  
**Portfolio Level:** Professional AI Developer Portfolio  
**Implementation Strategy:** 5 sequential phases  
**Primary Goal:** Build a complete working product from frontend to backend to AI pipeline, then test, document and deploy it.

---

# 0. PROJECT VISION

## Product Name

**EvidenceRAG**

## Tagline

> Ask your documents. Get answers backed by evidence.

## What are we building?

EvidenceRAG is a professional multi-document research assistant.

A user uploads research papers in PDF format and asks questions about them. The system:

1. receives the PDF,
2. extracts text page by page,
3. cleans and chunks the text,
4. generates embeddings,
5. stores chunks in a vector database,
6. retrieves relevant evidence for a question,
7. optionally reranks the evidence,
8. sends only relevant context to an LLM,
9. generates a grounded answer,
10. returns document/page citations,
11. lets the user inspect the exact evidence used.

The project must feel like a real AI product rather than a basic chatbot.

---

# 1. WHY THIS PROJECT IS STRONG FOR AN AI DEVELOPER PORTFOLIO

This single project demonstrates:

- Python
- FastAPI
- REST APIs
- React
- Tailwind CSS
- PDF processing
- NLP
- embeddings
- vector databases
- semantic search
- RAG
- LLM integration
- prompt engineering
- hallucination control
- source attribution
- evaluation
- testing
- logging
- Docker
- Git/GitHub
- professional UI/UX

The important point is that the project demonstrates **AI engineering**, not only an LLM API call.

---

# 2. FINAL TECHNOLOGY STACK

## Frontend

- React
- Vite
- Tailwind CSS
- JavaScript
- Axios or Fetch API
- Lucide Icons

## Backend

- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic
- python-multipart

## Document Processing

- PyMuPDF (`fitz`)

## AI / RAG

- Embedding model
- ChromaDB
- LLM provider
- Optional reranker

## Application Database

- SQLite for MVP metadata

## Testing

- pytest
- FastAPI TestClient

## Deployment

- Docker
- Docker Compose

## Version Control

- Git
- GitHub

---

# 3. HIGH-LEVEL PRODUCT ARCHITECTURE

```text
                         ┌──────────────────────┐
                         │        USER          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   REACT FRONTEND     │
                         │   Tailwind CSS       │
                         └──────────┬───────────┘
                                    │ REST / JSON
                                    ▼
                         ┌──────────────────────┐
                         │      FASTAPI         │
                         │       BACKEND        │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       Document Service       Chat/RAG Service      Health Service
              │                     │
              ▼                     ▼
        PDF Processing          Retrieval
              │                     │
              ▼                     ▼
          Chunking             Reranking
              │                     │
              ▼                     ▼
         Embeddings          Context Builder
              │                     │
              ▼                     ▼
          ChromaDB              LLM Service
              │                     │
              └──────────┬──────────┘
                         ▼
                Answer + Citations
                         │
                         ▼
                   FastAPI Response
                         │
                         ▼
                    React UI
```

---

# 4. COMPLETE RAG ARCHITECTURE

## Document Ingestion

```text
PDF Upload
    ↓
File Validation
    ↓
PDF Parser
    ↓
Page Extraction
    ↓
Text Cleaning
    ↓
Page Metadata
    ↓
Chunking
    ↓
Embedding Generation
    ↓
ChromaDB
```

## Question Answering

```text
User Question
    ↓
Question Validation
    ↓
Query Embedding
    ↓
Vector Similarity Search
    ↓
Top-K Chunks
    ↓
Score Filtering
    ↓
Optional Reranking
    ↓
Context Builder
    ↓
Grounded Prompt
    ↓
LLM
    ↓
Answer Validation
    ↓
Citation Validation
    ↓
Answer + Evidence + Sources
```

---

# 5. CORE PRODUCT FEATURES

## Document Features

- Upload one PDF
- Upload multiple PDFs
- Validate file type
- Validate file size
- Extract pages
- Track processing status
- Display page count
- Display chunk count
- Delete documents
- Prevent/handle duplicate documents

## RAG Features

- Embeddings
- Vector search
- Top-K retrieval
- Similarity threshold
- Optional reranking
- Context construction
- Grounded LLM answer
- Citation generation
- Evidence inspection
- No-evidence fallback

## Chat Features

- Ask questions
- Conversation history
- Follow-up questions
- New chat
- Clear conversation
- Source-aware answers

## Dashboard Features

- Documents
- Chat
- Sources
- System health
- Evaluation metrics

---

# 6. USER FLOW

```text
Open Application
       ↓
Landing / Empty State
       ↓
Upload PDF(s)
       ↓
Processing
       ↓
Indexed
       ↓
Research Workspace
       ↓
Ask Question
       ↓
Retrieve Evidence
       ↓
Generate Answer
       ↓
Show Sources
       ↓
Open Evidence
       ↓
Ask Follow-up
```

---

# 7. FINAL PROJECT STRUCTURE

```text
evidence-rag/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── documents.py
│   │   │   └── chat.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── health.py
│   │   │   ├── document.py
│   │   │   └── chat.py
│   │   │
│   │   ├── models/
│   │   │   ├── document.py
│   │   │   └── conversation.py
│   │   │
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   └── repositories.py
│   │   │
│   │   ├── services/
│   │   │   ├── pdf_service.py
│   │   │   ├── document_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── vector_service.py
│   │   │   ├── retrieval_service.py
│   │   │   ├── reranker_service.py
│   │   │   ├── llm_service.py
│   │   │   └── chat_service.py
│   │   │
│   │   ├── rag/
│   │   │   ├── chunker.py
│   │   │   ├── retriever.py
│   │   │   ├── context_builder.py
│   │   │   ├── prompt.py
│   │   │   └── citation.py
│   │   │
│   │   └── utils/
│   │       ├── file_utils.py
│   │       └── text_utils.py
│   │
│   ├── tests/
│   │   ├── test_health.py
│   │   ├── test_documents.py
│   │   ├── test_chunking.py
│   │   ├── test_retrieval.py
│   │   └── test_chat.py
│   │
│   ├── data/
│   │   ├── uploads/
│   │   └── chroma/
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── UploadZone.jsx
│   │   │   ├── DocumentCard.jsx
│   │   │   ├── DocumentList.jsx
│   │   │   ├── ChatMessage.jsx
│   │   │   ├── ChatInput.jsx
│   │   │   ├── SourceCard.jsx
│   │   │   ├── EvidencePanel.jsx
│   │   │   ├── StatusIndicator.jsx
│   │   │   ├── LoadingState.jsx
│   │   │   └── EmptyState.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Workspace.jsx
│   │   │   ├── Documents.jsx
│   │   │   ├── Evaluation.jsx
│   │   │   └── Settings.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── hooks/
│   │   │   └── useChat.js
│   │   │
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── Dockerfile
│
├── evaluation/
│   ├── dataset.json
│   ├── evaluate.py
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── evaluation.md
│
├── screenshots/
│   ├── dashboard.png
│   ├── documents.png
│   ├── chat.png
│   └── evidence.png
│
├── .gitignore
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

# 8. BACKEND RESPONSIBILITIES

## `main.py`

Only application setup:

- create FastAPI app
- register routers
- configure middleware
- startup/shutdown

Do NOT put RAG logic here.

## `api/`

Routes only.

Routes should call services.

## `services/`

Business logic.

## `rag/`

AI-specific RAG logic.

## `schemas/`

Pydantic request/response models.

## `db/`

Database/repository logic.

## `core/`

Configuration, logging and exceptions.

---

# 9. DOCUMENT DATA MODEL

```text
Document
──────────────
id
filename
file_path
file_hash
page_count
chunk_count
status
created_at
updated_at
```

Possible statuses:

```text
uploaded
processing
indexed
failed
```

---

# 10. CHUNK METADATA

Every chunk MUST preserve:

```json
{
  "document_id": "doc_123",
  "filename": "research-paper.pdf",
  "page": 7,
  "chunk_id": "doc_123_page_7_chunk_2"
}
```

This metadata is critical because citations depend on it.

---

# 11. CONVERSATION DATA

```text
Conversation
─────────────
id
created_at
updated_at
```

```text
Message
────────
id
conversation_id
role
content
created_at
```

Roles:

```text
user
assistant
```

---

# 12. API CONTRACT

Base URL:

```text
/api
```

## Health

```http
GET /api/health
```

Response:

```json
{
  "status": "ok",
  "backend": "connected",
  "vector_db": "ready",
  "llm": "configured"
}
```

---

## Upload Documents

```http
POST /api/documents/upload
```

Multipart form data.

Response:

```json
{
  "documents": [
    {
      "id": "doc_123",
      "filename": "paper.pdf",
      "status": "processing"
    }
  ]
}
```

---

## List Documents

```http
GET /api/documents
```

---

## Document Details

```http
GET /api/documents/{document_id}
```

---

## Delete Document

```http
DELETE /api/documents/{document_id}
```

---

## Chat

```http
POST /api/chat
```

Request:

```json
{
  "question": "What dataset was used?",
  "document_ids": ["doc_123"],
  "conversation_id": "conversation_001"
}
```

Response:

```json
{
  "conversation_id": "conversation_001",
  "answer": "The study used the HAM10000 dataset.",
  "grounded": true,
  "sources": [
    {
      "id": "source_1",
      "document_id": "doc_123",
      "filename": "paper.pdf",
      "page": 4,
      "score": 0.91,
      "evidence": "..."
    }
  ],
  "retrieval": {
    "top_k": 5,
    "returned": 2
  }
}
```

---

# 13. ERROR RESPONSE

All expected API errors should follow a consistent structure:

```json
{
  "error": {
    "code": "DOCUMENT_PROCESSING_FAILED",
    "message": "Unable to process the uploaded PDF."
  }
}
```

Example error codes:

```text
INVALID_FILE_TYPE
FILE_TOO_LARGE
DOCUMENT_PROCESSING_FAILED
EMBEDDING_FAILED
VECTOR_STORE_ERROR
RETRIEVAL_FAILED
LLM_ERROR
NO_EVIDENCE_FOUND
```

---

# 14. LLM SERVICE ABSTRACTION

Do not hard-code the whole application to one LLM provider.

Use:

```text
LLMService
    ↓
Provider implementation
```

The rest of the application should call:

```text
llm_service.generate(...)
```

rather than directly calling a provider from `chat.py`.

This allows future provider changes without rewriting the RAG system.

---

# 15. EMBEDDING SERVICE

Responsibilities:

- create document embeddings
- create query embeddings
- expose consistent interface
- handle API/model errors

Conceptual flow:

```text
Text
 ↓
Embedding Model
 ↓
Vector
 ↓
ChromaDB
```

Query:

```text
Question
 ↓
Embedding Model
 ↓
Query Vector
 ↓
Similarity Search
```

---

# 16. VECTOR DATABASE

Use **ChromaDB** for the initial implementation.

Store:

```text
embedding
document text
document ID
filename
page
chunk ID
```

Operations:

```text
create collection
add chunks
query chunks
delete document chunks
count vectors
```

---

# 17. CHUNKING REQUIREMENTS

Initial configuration:

```text
chunk size: approximately 700–1000 tokens/words
overlap: approximately 100–150 tokens/words
```

Implementation must prioritize paragraph/sentence boundaries where practical.

Every chunk must preserve page information.

Future upgrade:

```text
semantic chunking
section-aware chunking
table-aware extraction
```

Do not implement complex chunking until the MVP works.

---

# 18. RETRIEVAL

Initial:

```text
TOP_K = 5
```

Process:

```text
Question
 ↓
Query embedding
 ↓
ChromaDB
 ↓
Top 5 chunks
 ↓
Score filtering
 ↓
Relevant evidence
```

Use a configurable similarity threshold.

Example:

```env
TOP_K=5
SIMILARITY_THRESHOLD=0.35
```

The threshold must be configurable rather than hard-coded.

---

# 19. OPTIONAL RERANKING

Architecture should support:

```text
Vector Search
      ↓
Top 10 candidates
      ↓
Reranker
      ↓
Top 4 evidence chunks
```

Reranking can remain disabled by default if it introduces unnecessary setup complexity.

The project must still work without a reranker.

---

# 20. CONTEXT BUILDER

The context builder converts retrieved chunks into LLM context.

Example:

```text
SOURCE 1
Document: paper.pdf
Page: 4

[retrieved evidence]


SOURCE 2
Document: survey.pdf
Page: 8

[retrieved evidence]
```

Limit total context to avoid unnecessarily large prompts.

---

# 21. GROUNDED PROMPT REQUIREMENTS

The system prompt should enforce:

```text
You are an evidence-based research assistant.

Use ONLY the provided context to answer the user's question.

Rules:
1. Do not invent information.
2. Do not use unsupported facts.
3. If evidence is insufficient, clearly say so.
4. Use the supplied source metadata for citations.
5. Do not create citations for sources that were not retrieved.
6. Prefer concise and accurate answers.
```

---

# 22. NO-EVIDENCE BEHAVIOR

This is mandatory.

If the retrieval score is below the threshold:

```json
{
  "answer": "I couldn't find sufficient evidence in the uploaded documents to answer this question.",
  "grounded": false,
  "sources": []
}
```

Do NOT allow the LLM to confidently answer from general knowledge when the application is supposed to answer from uploaded documents.

---

# 23. CITATION SYSTEM

Each source:

```json
{
  "id": "source_1",
  "document_id": "doc_123",
  "filename": "paper.pdf",
  "page": 4,
  "score": 0.91,
  "evidence": "..."
}
```

Frontend display:

```text
Sources
────────────────────
[1] paper.pdf
    Page 4
    Relevance 91%

[2] survey.pdf
    Page 8
    Relevance 86%
```

Clicking a source opens its evidence.

---

# 24. FRONTEND DESIGN SYSTEM

## Design Style

The frontend must look like a premium AI SaaS/research application.

Characteristics:

- clean
- minimal
- professional
- modern
- excellent spacing
- readable typography
- subtle borders
- strong hierarchy
- responsive
- dark-first or dark/light supported
- restrained animations

Avoid:

- default browser forms
- giant gradients
- excessive neon
- clutter
- too many cards
- unnecessary animations

---

# 25. FRONTEND INFORMATION ARCHITECTURE

```text
EvidenceRAG
│
├── New Chat
├── Research Workspace
├── Documents
├── Evaluation
└── Settings
```

---

# 26. LANDING / EMPTY STATE

Display:

```text
EvidenceRAG

Evidence-based research assistant

Upload your research papers and ask questions
with answers backed by source evidence.

[ Upload PDFs ]
```

Feature cards:

```text
Fast Retrieval
Source Citations
Evidence-Backed Answers
```

---

# 27. MAIN WORKSPACE

```text
┌─────────────────────────────────────────────────────────┐
│ EvidenceRAG                              System ● Ready │
├───────────────┬─────────────────────────────────────────┤
│               │                                         │
│ + New Chat    │  Research Assistant                     │
│               │                                         │
│ Documents     │  Ask questions about your papers        │
│               │                                         │
│ paper.pdf     │  ┌───────────────────────────────────┐  │
│ survey.pdf    │  │ User question                     │  │
│               │  └───────────────────────────────────┘  │
│ Evaluation    │                                         │
│               │  AI answer...                           │
│ Settings      │                                         │
│               │  Sources                                │
│ System Status │  [paper.pdf · Page 4 · 91%]             │
│ ● Backend     │                                         │
│ ● Vector DB   │  [ Ask a research question... ] [Send]  │
│ ● LLM         │                                         │
└───────────────┴─────────────────────────────────────────┘
```

---

# 28. UPLOAD EXPERIENCE

Upload zone:

```text
┌─────────────────────────────────┐
│         Upload Documents        │
│                                 │
│ Drag & drop PDF files here      │
│ or                              │
│        [ Choose Files ]         │
│                                 │
│ PDF · Maximum configured size   │
└─────────────────────────────────┘
```

After upload:

```text
paper.pdf

Processing...
██████████████░░░░
```

Then:

```text
✓ Indexed
```

---

# 29. DOCUMENT CARD

Each document card should show:

```text
📄 paper.pdf

Indexed
12 pages
84 chunks

[Delete]
```

---

# 30. CHAT MESSAGE

User:

```text
What dataset was used by the proposed model?
```

Assistant:

```text
The proposed model was evaluated using the
HAM10000 dataset.

Sources
──────────────
paper.pdf · Page 4 · 91%
```

---

# 31. EVIDENCE PANEL

When the user clicks a source:

```text
SOURCE EVIDENCE

paper.pdf
Page 4

Relevance
91%

────────────────────────────

The dataset contains...
[retrieved evidence text]

────────────────────────────

[Close]
```

---

# 32. LOADING STATES

Use meaningful states:

```text
Uploading document...
```

```text
Extracting pages...
```

```text
Creating embeddings...
```

```text
Searching evidence...
```

```text
Generating grounded answer...
```

---

# 33. EMPTY STATES

No documents:

```text
No research papers yet.

Upload a PDF to start asking questions.
```

No conversation:

```text
Start your research

Ask a question about your uploaded documents.
```

No evidence:

```text
No reliable evidence found.

Try rephrasing your question or upload
a relevant document.
```

---

# 34. SYSTEM STATUS

Sidebar/footer:

```text
System Status

● Backend       Connected
● Vector DB     Ready
● LLM           Configured
```

If something fails:

```text
● Backend       Disconnected
● Vector DB     Ready
● LLM           Not configured
```

Use accessible status indicators and text, not color alone.

---

# 35. SETTINGS PAGE

MVP settings:

```text
Model
Embedding Model
Top-K Retrieval
Similarity Threshold
```

These should be informational/configurable where practical.

Do not expose API keys in the frontend.

---

# 36. EVALUATION PAGE

Display:

```text
RAG Evaluation

Retrieval Hit Rate
89%

Citation Accuracy
94%

Faithfulness
91%

Average Response Time
2.1s
```

Below:

```text
Evaluation Runs
────────────────────
Run #04     91%
Run #03     88%
Run #02     84%
Run #01     79%
```

Never invent portfolio metrics.

Only display metrics produced by actual tests/evaluation.

---

# 37. PHASE PLAN

The complete project MUST be built in exactly these five phases.

---

# PHASE 1 — FOUNDATION + FULL BACKEND DOCUMENT PIPELINE

## Goal

Build the complete backend foundation and make PDF ingestion fully functional.

At the end of Phase 1:

```text
Frontend not required yet
Backend running
PDF upload working
PDF extraction working
Chunking working
Metadata working
Document database working
Tests working
```

## Tasks

### 1. Repository Setup

Create:

```text
evidence-rag/
backend/
frontend/
evaluation/
docs/
```

### 2. Backend Environment

Create Python virtual environment.

Install:

```text
fastapi
uvicorn
pydantic
python-multipart
pymupdf
chromadb
python-dotenv
pytest
httpx
```

Only add dependencies when needed.

### 3. FastAPI

Create:

```text
backend/app/main.py
```

Implement:

- FastAPI instance
- router registration
- CORS configuration
- startup configuration

### 4. Configuration

Create:

```text
core/config.py
```

Read values from `.env`.

### 5. Health Endpoint

Implement:

```text
GET /api/health
```

### 6. PDF Upload

Implement:

```text
POST /api/documents/upload
```

Requirements:

- PDF validation
- filename sanitization
- file size validation
- unique document ID
- local file storage
- processing status

### 7. PDF Extraction

For every page extract:

```text
page number
text
```

### 8. Text Cleaning

Clean:

- excessive whitespace
- invalid characters
- unnecessary blank lines

Do not destroy meaningful content.

### 9. Chunking

Implement page-aware chunking.

### 10. Metadata

Each chunk must retain:

```text
document_id
filename
page
chunk_id
```

### 11. SQLite Metadata

Store:

```text
document
status
page_count
chunk_count
created_at
```

### 12. Document APIs

Implement:

```text
GET /api/documents
GET /api/documents/{id}
DELETE /api/documents/{id}
```

### 13. Error Handling

Implement custom exceptions and structured errors.

### 14. Logging

Add:

```text
document_uploaded
document_processed
chunks_created
document_processing_failed
```

### 15. Tests

Test:

- health
- valid PDF
- invalid file
- chunking
- metadata
- document listing
- document deletion

## Phase 1 Acceptance Criteria

```text
[ ] Backend starts successfully
[ ] /api/health works
[ ] PDF upload works
[ ] Multiple PDFs can be uploaded
[ ] Invalid files are rejected
[ ] Pages are extracted
[ ] Chunks are created
[ ] Page metadata is preserved
[ ] Document records are stored
[ ] Documents can be listed
[ ] Documents can be deleted
[ ] Tests pass
```

---

# PHASE 2 — COMPLETE RAG + AI ENGINE

## Goal

Turn the backend into a complete AI-powered RAG system.

At the end:

```text
PDF
 ↓
Chunk
 ↓
Embedding
 ↓
ChromaDB

Question
 ↓
Retrieval
 ↓
Context
 ↓
LLM
 ↓
Grounded Answer
 ↓
Citation
```

## Tasks

### 1. Embedding Service

Create:

```text
services/embedding_service.py
```

Responsibilities:

- document embeddings
- query embeddings
- model configuration
- error handling

### 2. ChromaDB

Create:

```text
services/vector_service.py
```

Implement:

- initialize database
- collection creation
- insert vectors
- similarity search
- delete document vectors

### 3. Connect Ingestion

Phase 1 pipeline becomes:

```text
Upload
 ↓
Extract
 ↓
Chunk
 ↓
Embed
 ↓
ChromaDB
 ↓
Indexed
```

### 4. Retrieval Service

Implement:

```text
services/retrieval_service.py
```

Input:

```text
question
```

Output:

```text
relevant chunks + metadata + score
```

### 5. Similarity Threshold

Use:

```env
TOP_K=5
SIMILARITY_THRESHOLD=0.35
```

Make configurable.

### 6. Reranker

Create abstraction:

```text
reranker_service.py
```

MVP can return candidates unchanged when reranking is disabled.

### 7. Context Builder

Create:

```text
rag/context_builder.py
```

### 8. LLM Service

Create provider abstraction.

### 9. Grounded Prompt

Implement strict evidence-only behavior.

### 10. Citation Engine

Create:

```text
rag/citation.py
```

Only retrieved sources can become citations.

### 11. Chat Service

Create:

```text
services/chat_service.py
```

Pipeline:

```text
Question
 ↓
Retrieve
 ↓
Filter
 ↓
Rerank
 ↓
Build Context
 ↓
LLM
 ↓
Validate
 ↓
Citations
```

### 12. Chat API

Implement:

```text
POST /api/chat
```

### 13. Conversation History

Store current session messages.

### 14. No-Evidence Protection

Mandatory.

## Phase 2 Acceptance Criteria

```text
[ ] PDF chunks have embeddings
[ ] Vectors stored in ChromaDB
[ ] Questions retrieve relevant chunks
[ ] Scores are returned
[ ] Threshold works
[ ] Context is built
[ ] LLM receives only relevant context
[ ] Grounded answer works
[ ] Citations work
[ ] Evidence is returned
[ ] No-evidence fallback works
[ ] Follow-up conversation works
[ ] Chat API works
[ ] Tests pass
```

---

# PHASE 3 — PROFESSIONAL FRONTEND + FULL INTEGRATION

## Goal

Build a portfolio-quality frontend and connect it to the existing backend.

Do NOT rewrite the backend just to change UI.

## Tasks

### 1. React Setup

Create React + Vite application.

### 2. Tailwind Setup

Configure Tailwind.

### 3. API Layer

Create:

```text
frontend/src/services/api.js
```

All API calls should be centralized.

### 4. Application Shell

Build:

```text
Sidebar
Header
Main Workspace
```

### 5. Upload UI

Implement:

- drag/drop
- file picker
- validation
- progress
- processing status

### 6. Documents Page

Display:

- filename
- status
- page count
- chunk count
- delete action

### 7. Chat Workspace

Implement:

- user messages
- assistant messages
- markdown rendering
- loading
- errors
- source cards

### 8. Evidence Drawer

Click source → show:

```text
document
page
score
evidence
```

### 9. New Chat

Reset conversation.

### 10. System Status

Call health endpoint.

### 11. Responsive Design

Must work on:

- desktop
- laptop
- tablet

### 12. Accessibility

- keyboard focus
- readable contrast
- semantic buttons
- meaningful labels
- status text

### 13. Frontend Error Handling

Examples:

```text
Upload failed
Backend unavailable
LLM unavailable
No evidence found
```

### 14. Integration

Verify:

```text
Upload
 ↓
Backend
 ↓
Processing
 ↓
Indexed
 ↓
Question
 ↓
RAG
 ↓
Answer
 ↓
Sources
 ↓
Evidence
```

## Phase 3 Acceptance Criteria

```text
[ ] React app runs
[ ] Backend connection works
[ ] Upload works from UI
[ ] Processing status appears
[ ] Documents appear
[ ] Chat works
[ ] Answers render correctly
[ ] Sources appear
[ ] Evidence panel works
[ ] Delete works
[ ] New chat works
[ ] Health status works
[ ] Loading states work
[ ] Error states work
[ ] Responsive UI works
```

---

# PHASE 4 — EVALUATION + TESTING + DOCKER + PRODUCTION POLISH

## Goal

Turn the working application into a reliable portfolio project.

## 1. Evaluation Dataset

Create:

```text
evaluation/dataset.json
```

Example:

```json
[
  {
    "question": "What dataset was used?",
    "expected_source": "paper.pdf",
    "expected_page": 4
  }
]
```

Create at least 10–20 meaningful questions using real test PDFs.

## 2. Retrieval Evaluation

Measure:

```text
Hit@K
```

Question:

> Did the correct evidence appear in the retrieved results?

## 3. Citation Accuracy

Check whether citations point to actual retrieved sources.

## 4. Faithfulness

Check whether the answer is supported by retrieved evidence.

Use an LLM evaluator only as an evaluation helper; do not treat it as perfect ground truth.

## 5. Latency

Measure:

```text
retrieval latency
LLM latency
total response time
```

## 6. Evaluation Script

Create:

```text
evaluation/evaluate.py
```

Output:

```text
Retrieval Hit Rate: 89%
Citation Accuracy: 94%
Faithfulness: 91%
Average Latency: 2.1s
```

Use actual measured values.

## 7. Backend Tests

Run:

```bash
pytest
```

## 8. Integration Tests

Test:

```text
Upload
 ↓
Index
 ↓
Chat
 ↓
Citation
```

## 9. Docker

Create backend Dockerfile.

Create frontend Dockerfile.

Create:

```text
docker-compose.yml
```

Services:

```text
backend
frontend
```

Use a persistent volume for:

```text
backend/data
```

## 10. Production Configuration

Ensure:

- secrets in environment variables
- debug disabled in production
- configurable CORS
- upload size limit
- clean logs

## 11. Security Review

Check:

```text
[ ] No API keys in Git
[ ] No .env committed
[ ] No personal documents
[ ] File validation
[ ] File size limit
[ ] Filename sanitization
[ ] Error sanitization
```

## Phase 4 Acceptance Criteria

```text
[ ] Evaluation dataset exists
[ ] Retrieval metrics work
[ ] Citation evaluation works
[ ] Faithfulness evaluation works
[ ] Latency measured
[ ] Unit tests pass
[ ] Integration tests pass
[ ] Docker build works
[ ] Docker Compose works
[ ] Persistent data works
[ ] No secrets committed
```

---

# PHASE 5 — GITHUB + DOCUMENTATION + PORTFOLIO + LINKEDIN

## Goal

Turn the project into professional proof of work.

---

# 5.1 README STRUCTURE

Create:

```text
README.md
```

Sections:

```text
EvidenceRAG
├── Overview
├── Why EvidenceRAG?
├── Features
├── Demo
├── Architecture
├── RAG Pipeline
├── Tech Stack
├── Project Structure
├── Installation
├── Environment Variables
├── API
├── Evaluation
├── Screenshots
├── Challenges
├── Engineering Decisions
├── Limitations
├── Future Improvements
└── License
```

---

# 5.2 ARCHITECTURE DOCUMENT

Create:

```text
docs/architecture.md
```

Explain:

- frontend
- backend
- ingestion
- embeddings
- vector database
- retrieval
- reranking
- context
- LLM
- citations

---

# 5.3 API DOCUMENT

Create:

```text
docs/api.md
```

Document:

```text
GET /api/health
POST /api/documents/upload
GET /api/documents
GET /api/documents/{id}
DELETE /api/documents/{id}
POST /api/chat
```

---

# 5.4 EVALUATION DOCUMENT

Create:

```text
docs/evaluation.md
```

Explain:

- dataset
- metrics
- methodology
- results
- failure cases
- improvements

---

# 5.5 SCREENSHOTS

Capture:

```text
dashboard.png
documents.png
chat.png
evidence.png
evaluation.png
```

Do not use fake screenshots.

---

# 5.6 GITHUB DESCRIPTION

Use:

> Evidence-based multi-document RAG research assistant with PDF ingestion, semantic retrieval, grounded LLM responses, source citations, evidence inspection, evaluation, and a professional React interface.

---

# 5.7 GITHUB TOPICS

```text
ai
artificial-intelligence
rag
retrieval-augmented-generation
generative-ai
llm
llm-applications
python
fastapi
react
chromadb
vector-database
embeddings
nlp
machine-learning
```

---

# 5.8 GIT COMMIT STRATEGY

Use meaningful commits:

```text
feat: initialize FastAPI backend
feat: add PDF document ingestion
feat: implement page-aware chunking
feat: add document metadata storage
feat: integrate embeddings
feat: integrate ChromaDB
feat: implement semantic retrieval
feat: add grounded LLM responses
feat: add citation engine
feat: build research workspace UI
feat: add document management
feat: add evidence panel
feat: add evaluation pipeline
test: add backend test suite
test: add RAG integration tests
chore: dockerize application
docs: add architecture documentation
docs: improve README
```

Do not make one huge commit such as:

```text
final project
```

---

# 5.9 PORTFOLIO WEBSITE CASE STUDY

Project card:

```text
EvidenceRAG

A multi-document AI research assistant that
answers questions from research papers using
Retrieval-Augmented Generation and provides
page-level evidence for grounded responses.

RAG · LLM · FastAPI · React · ChromaDB · Python
```

Buttons:

```text
Live Demo
GitHub
Case Study
```

Case study:

```text
Problem
 ↓
Solution
 ↓
Architecture
 ↓
Implementation
 ↓
Evaluation
 ↓
Results
 ↓
Lessons Learned
```

---

# 5.10 LINKEDIN CONTENT PLAN

Do not publish only one generic post.

Create several posts from the same project.

## Post 1 — Launch

Hook:

> What if an AI assistant could answer questions from research papers — and show exactly where the answer came from?

Discuss:

- EvidenceRAG
- RAG
- citations
- evidence
- technology

## Post 2 — Architecture

Show:

```text
PDF
 ↓
Chunking
 ↓
Embeddings
 ↓
Vector Search
 ↓
Context
 ↓
LLM
 ↓
Evidence
```

Explain each step.

## Post 3 — Hallucination

Topic:

> What happens when a RAG system cannot find the answer?

Explain:

- similarity threshold
- no-evidence behavior
- grounded generation

## Post 4 — Evaluation

Show actual metrics.

Explain:

- Hit@K
- citation accuracy
- faithfulness
- latency

## Post 5 — UI Demo

Short screen recording showing:

```text
Upload PDF
 ↓
Ask Question
 ↓
Answer
 ↓
Click Source
 ↓
Inspect Evidence
```

---

# 6. ENVIRONMENT VARIABLES

Backend `.env.example`:

```env
APP_ENV=development
DEBUG=true

LLM_PROVIDER=
LLM_API_KEY=
LLM_MODEL=

EMBEDDING_PROVIDER=
EMBEDDING_MODEL=

VECTOR_DB_PATH=./data/chroma

TOP_K=5
SIMILARITY_THRESHOLD=0.35
MAX_UPLOAD_SIZE_MB=20

FRONTEND_URL=http://localhost:5173
```

Frontend `.env.example`:

```env
VITE_API_URL=http://localhost:8000/api
```

Never commit actual `.env`.

---

# 7. LOCAL DEVELOPMENT COMMANDS

## Backend

Create virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 8. FRONTEND COMMANDS

From:

```text
frontend/
```

Install:

```bash
npm install
```

Run:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 9. DOCKER RUN

From root:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

---

# 10. COMPLETE END-TO-END TEST

Perform exactly this test before calling the project complete.

```text
1. Start backend
2. Start frontend
3. Open browser
4. Verify system status
5. Upload research paper
6. Verify processing status
7. Verify Indexed status
8. Confirm document appears
9. Ask a factual question
10. Confirm answer
11. Confirm source citation
12. Open source
13. Inspect evidence
14. Ask follow-up question
15. Upload second paper
16. Ask cross-document question
17. Confirm multiple sources
18. Delete one document
19. Confirm deletion
20. Restart backend
21. Confirm vector data persists
22. Run pytest
23. Run evaluation
24. Build Docker image
25. Run Docker Compose
26. Repeat basic user flow
```

---

# 11. CROSS-DOCUMENT DEMO

Upload:

```text
paper_A.pdf
paper_B.pdf
survey.pdf
```

Ask:

> Compare the datasets used by the studies.

Expected UI:

```text
Comparison

paper_A.pdf
Dataset: ...
Page: 4

paper_B.pdf
Dataset: ...
Page: 5

survey.pdf
Dataset discussion: ...
Page: 8
```

This is a strong portfolio demonstration because it proves the system is not just answering from one static document.

---

# 12. FAILURE CASES TO TEST

## Case 1 — Unsupported file

Upload:

```text
image.png
```

Expected:

```text
Invalid file type.
Only PDF files are supported.
```

## Case 2 — Corrupted PDF

Expected:

```text
Unable to process this PDF.
```

## Case 3 — Question unrelated to documents

Expected:

```text
I couldn't find sufficient evidence in the
uploaded documents to answer this question.
```

## Case 4 — Backend offline

Expected frontend:

```text
Backend unavailable.
Please check the server.
```

## Case 5 — LLM unavailable

Expected:

```text
The AI service is currently unavailable.
```

## Case 6 — Empty question

Expected:

```text
Please enter a question.
```

---

# 13. AI QUALITY RULES

The AI system must:

```text
[ ] Prefer evidence over general knowledge
[ ] Avoid unsupported claims
[ ] Never fabricate citations
[ ] Preserve page metadata
[ ] Clearly communicate uncertainty
[ ] Return structured sources
[ ] Handle retrieval failure
```

---

# 14. ENGINEERING RULES

The implementation must:

```text
[ ] Keep routes thin
[ ] Use service classes/modules
[ ] Use Pydantic schemas
[ ] Use environment variables
[ ] Avoid hardcoded secrets
[ ] Use logging
[ ] Use meaningful exceptions
[ ] Add tests
[ ] Keep dependencies reasonable
[ ] Keep code modular
```

Avoid:

```text
[ ] 1000-line main.py
[ ] hardcoded API keys
[ ] duplicated API logic
[ ] silent exception handling
[ ] fake evaluation numbers
[ ] unnecessary dependencies
```

---

# 15. CLAUDE IMPLEMENTATION RULES

Use Claude as the implementation assistant, but implement phase by phase.

Give Claude the complete `PROJECT_REQUIREMENTS.md` first.

Claude must follow these rules:

```text
1. Read the complete requirements before coding.
2. Implement only the requested phase.
3. Do not skip architecture.
4. Do not create a toy chatbot.
5. Keep frontend and backend modular.
6. Do not change API contracts without a clear reason.
7. Never hardcode secrets.
8. Preserve document/page metadata.
9. Never fabricate citations.
10. Add error handling.
11. Add tests.
12. Run the application after implementation.
13. Report changed files.
14. Explain important code.
15. Report exact run commands.
16. Fix errors before moving to the next phase.
17. Do not add unnecessary features.
18. Do not replace working architecture just because another framework is available.
```

---

# 16. CLAUDE PROMPT — PHASE 1

```text
Read PROJECT_REQUIREMENTS.md completely.

Implement ONLY PHASE 1.

Build the backend foundation and document ingestion pipeline.

Requirements:
- FastAPI
- configuration
- health endpoint
- PDF upload
- PDF validation
- file size validation
- filename sanitization
- page-aware PDF extraction
- text cleaning
- chunking
- chunk metadata
- SQLite document metadata
- document list endpoint
- document details endpoint
- document delete endpoint
- logging
- structured errors
- pytest tests

Do not build the frontend.
Do not implement the LLM chat yet.
Do not implement advanced RAG yet.

After coding:
1. Show the complete backend structure.
2. Explain each important file.
3. Run tests.
4. Fix failures.
5. Give exact commands to run.
6. Give an API testing example.
7. Confirm the Phase 1 acceptance criteria.
```

---

# 17. CLAUDE PROMPT — PHASE 2

```text
Read PROJECT_REQUIREMENTS.md completely.

Phase 1 is complete and working.

Implement ONLY PHASE 2.

Build the complete RAG and AI engine.

Requirements:
- embedding service
- ChromaDB
- vector storage
- query embeddings
- semantic retrieval
- top-k retrieval
- similarity threshold
- reranker abstraction
- context builder
- LLM service abstraction
- grounded prompt
- citation engine
- no-evidence behavior
- chat service
- conversation handling
- POST /api/chat
- tests

Important:
- preserve document/page metadata
- never fabricate citations
- do not answer unsupported questions confidently
- keep LLM provider behind a service abstraction
- keep API routes thin

After coding:
1. Explain the complete RAG pipeline.
2. Show the data flow.
3. Explain retrieval.
4. Explain embeddings.
5. Explain citations.
6. Run tests.
7. Fix all failures.
8. Give exact run commands.
9. Give a manual RAG test procedure.
10. Confirm Phase 2 acceptance criteria.
```

---

# 18. CLAUDE PROMPT — PHASE 3

```text
Read PROJECT_REQUIREMENTS.md completely.

Phases 1 and 2 are complete.

Implement ONLY PHASE 3.

Build the complete professional React + Vite + Tailwind frontend.

Requirements:
- application shell
- sidebar
- header
- landing/empty state
- upload zone
- document cards
- document list
- research workspace
- chat messages
- chat input
- source cards
- evidence drawer
- loading states
- error states
- empty states
- system status
- evaluation page
- settings page
- responsive design
- accessibility
- API service layer

Connect to the existing FastAPI APIs.

Do not rewrite working backend logic.

The interface should look like a polished professional AI research product.

After coding:
1. Show frontend structure.
2. Explain components.
3. Start frontend.
4. Verify backend integration.
5. Test upload.
6. Test chat.
7. Test citations.
8. Test evidence panel.
9. Test deletion.
10. Fix integration bugs.
```

---

# 19. CLAUDE PROMPT — PHASE 4

```text
Read PROJECT_REQUIREMENTS.md completely.

Phases 1, 2 and 3 are complete.

Implement ONLY PHASE 4.

Requirements:
- evaluation dataset
- retrieval Hit@K
- citation accuracy
- faithfulness evaluation
- latency measurement
- evaluation script
- evaluation documentation
- unit tests
- integration tests
- improved logging
- improved error handling
- Dockerfile for backend
- Dockerfile for frontend
- docker-compose.yml
- persistent data
- production configuration
- security review

Do not add unnecessary product features.

Do not invent evaluation metrics.

Run:
- all tests
- evaluation
- Docker build
- Docker Compose

Fix failures before finishing.
```

---

# 20. CLAUDE PROMPT — PHASE 5

```text
Read PROJECT_REQUIREMENTS.md completely.

The application is fully working.

Implement ONLY PHASE 5.

Prepare the project for GitHub, portfolio and LinkedIn.

Create/update:
- README.md
- docs/architecture.md
- docs/api.md
- docs/evaluation.md
- project screenshots guidance
- GitHub project description
- GitHub topics
- setup instructions
- engineering decisions
- limitations
- future improvements

Audit the repository for:
- secrets
- .env files
- debug code
- broken imports
- unnecessary files
- poor naming
- missing documentation
- hardcoded paths

Do not change working AI behavior unless a real issue is discovered.

At the end:
1. Give final project tree.
2. Give Git commands.
3. Give GitHub README outline.
4. Give portfolio project description.
5. Give LinkedIn launch post outline.
6. Confirm final Definition of Done.
```

---

# 21. DEFINITION OF DONE

## Backend

```text
[ ] FastAPI working
[ ] Health endpoint
[ ] PDF upload
[ ] Multi-PDF upload
[ ] PDF validation
[ ] Page extraction
[ ] Chunking
[ ] Metadata
[ ] Embeddings
[ ] ChromaDB
[ ] Retrieval
[ ] Threshold
[ ] LLM
[ ] Grounded prompt
[ ] Citations
[ ] Evidence
[ ] No-evidence handling
[ ] Conversations
[ ] Delete document
[ ] Logging
[ ] Error handling
```

## Frontend

```text
[ ] React
[ ] Vite
[ ] Tailwind
[ ] Sidebar
[ ] Workspace
[ ] Upload
[ ] Documents
[ ] Chat
[ ] Sources
[ ] Evidence panel
[ ] Loading states
[ ] Error states
[ ] Empty states
[ ] Health status
[ ] Evaluation
[ ] Settings
[ ] Responsive
[ ] Accessible
```

## Quality

```text
[ ] Unit tests
[ ] Integration tests
[ ] Evaluation dataset
[ ] Retrieval evaluation
[ ] Citation evaluation
[ ] Faithfulness evaluation
[ ] Latency measurement
[ ] Docker
[ ] Docker Compose
[ ] Persistent storage
```

## Portfolio

```text
[ ] README
[ ] Architecture diagram
[ ] API documentation
[ ] Evaluation documentation
[ ] Screenshots
[ ] Demo
[ ] GitHub topics
[ ] Clean commits
[ ] Portfolio case study
[ ] LinkedIn launch content
```

---

# 22. FUTURE IMPROVEMENTS

Only after the complete MVP works:

```text
1. Hybrid BM25 + vector search
2. Cross-encoder reranking
3. Semantic chunking
4. Query rewriting
5. Streaming responses
6. PDF page preview
7. Table extraction
8. Background ingestion
9. PostgreSQL
10. Qdrant
11. Redis caching
12. Authentication
13. Multi-user workspaces
14. Cloud deployment
```

Do not add these before the core project is stable.

---

# 23. INTERVIEW PREPARATION

After completing the project, be able to explain:

## RAG

- What is RAG?
- Why RAG instead of fine-tuning?
- Why embeddings?
- Why vector search?
- How does chunking affect retrieval?
- What is top-k?
- What is reranking?
- What causes hallucination?
- How do you handle missing evidence?

## Backend

- Why FastAPI?
- Why service architecture?
- How are errors handled?
- How is PDF validation implemented?
- How is the API structured?

## Vector DB

- Why ChromaDB?
- What metadata is stored?
- How is document deletion handled?
- How does similarity search work?

## LLM

- How is context constructed?
- How do you reduce hallucination?
- How do you handle long context?
- Why abstract the LLM provider?

## Evaluation

- How do you know retrieval works?
- What is Hit@K?
- What is faithfulness?
- How do you measure citation accuracy?
- How would you improve low retrieval accuracy?

## Scaling

- What happens with 100,000 documents?
- How would you support multiple users?
- How would you reduce latency?
- How would you move from ChromaDB to Qdrant?
- How would you deploy this to the cloud?

---

# 24. FINAL PROJECT STORY

When someone opens the repository, they should understand this story:

```text
Problem
Research papers are difficult to search manually.
        ↓
Solution
EvidenceRAG lets users ask questions about PDFs.
        ↓
AI
RAG retrieves relevant evidence.
        ↓
Reliability
Answers are grounded and citations are provided.
        ↓
Transparency
Users can inspect the exact evidence.
        ↓
Engineering
FastAPI + React + Vector DB + LLM + Testing.
        ↓
Quality
Evaluation + logging + error handling.
        ↓
Deployment
Dockerized application.
        ↓
Portfolio
GitHub + Portfolio + LinkedIn.
```

---

# 25. FINAL RULE FOR IMPLEMENTATION

**Do not implement all five phases at once.**

Use this sequence:

```text
PHASE 1
Foundation + Backend
       ↓
RUN
       ↓
TEST
       ↓
UNDERSTAND
       ↓
PHASE 2
RAG + AI
       ↓
RUN
       ↓
TEST
       ↓
UNDERSTAND
       ↓
PHASE 3
Frontend + Integration
       ↓
RUN
       ↓
TEST
       ↓
UNDERSTAND
       ↓
PHASE 4
Evaluation + Docker
       ↓
RUN
       ↓
TEST
       ↓
PHASE 5
GitHub + Portfolio + LinkedIn
```

**The project is complete only when frontend + backend + AI + testing + evaluation + deployment all work together.**

---

# PROJECT STATUS

```text
PHASE 1  ☐ Foundation + Backend
PHASE 2  ☐ RAG + AI Engine
PHASE 3  ☐ Professional Frontend
PHASE 4  ☐ Evaluation + Docker
PHASE 5  ☐ GitHub + Portfolio + LinkedIn

FINAL STATUS: ☐ PORTFOLIO READY
```
