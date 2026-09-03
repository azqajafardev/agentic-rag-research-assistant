# How the RAG Pipeline Works (Interview Guide)

A plain-language walkthrough of what actually happens between a PDF landing
in `backend/data/uploads` and an answer showing up in the chat UI, plus the
reasoning behind the main design decisions. See [architecture.md](architecture.md)
for the diagrammed version of the same flow.

## The pipeline, step by step

1. **PDF → text (PyMuPDF).** Each page is extracted separately, not as one
   blob, so page numbers survive into every later stage.
2. **Chunking.** Each page's text is split into ~800-word windows with a
   120-word overlap. Overlap exists so a fact split across a chunk boundary
   still appears whole in at least one chunk. Chunking never crosses a page
   boundary - a chunk's page number is never ambiguous.
3. **Embeddings.** Each chunk is converted to a vector with a local
   `all-MiniLM-L6-v2` ONNX model (no API call, no key). The question is
   embedded with the same model at query time.
4. **Vector storage (ChromaDB).** Vectors are stored with a deterministic id
   (`{document_id}_page_{n}_chunk_{n}`) and metadata (`document_id`,
   `filename`, `page`) in a cosine-similarity collection.
5. **Semantic retrieval.** The question's vector is compared against every
   chunk vector; the top-K closest chunks come back, each with a similarity
   score.
6. **Similarity threshold.** Chunks below `SIMILARITY_THRESHOLD` (0.35) are
   discarded. If nothing survives, retrieval returns empty - see
   [No-evidence protection](#what-happens-when-evidence-is-missing).
7. **Reranking.** A hook (`RerankerService`) that can re-score the
   surviving chunks with a cross-encoder for higher precision. Off by
   default (pass-through) because it adds latency and a model dependency
   that the current chunk counts don't yet justify - see
   [Why page-aware chunks?](#why-page-aware-chunks) for the related
   precision/recall tradeoff.
8. **Context construction.** Surviving chunks are formatted into numbered
   `SOURCE` blocks and truncated to `MAX_CONTEXT_CHARS` so the prompt stays
   bounded regardless of how many chunks matched.
9. **Grounded LLM call.** Claude receives a system prompt that instructs it
   to answer only from the numbered sources and to cite them, plus the
   context and a capped slice of conversation history.
10. **Citations.** Built from the retrieved chunks *before* the LLM runs,
    not parsed out of its output - so a citation always points at a real
    `document_id` + `page` the retrieval step actually found.

## Why RAG?

An LLM alone only knows what was in its training data, and it will produce
a fluent, confident answer regardless of whether it actually knows
something - that's hallucination. RAG grounds every answer in text
retrieved from the user's own documents at query time, so the system can
answer about documents the model has never seen, and - just as important -
can also *refuse* to answer when those documents don't cover the question.

## Why ChromaDB?

It's an embedded, persistent vector database with no separate server
process to run or operate - a good fit for a project this size. It
supports cosine similarity search out of the box, persists to disk between
restarts, and its Python client integrates directly with a manually
computed embedding pipeline (this project intentionally computes embeddings
itself rather than using ChromaDB's implicit embedding-function-at-query-time
path, so the exact same embedding call is used for both indexing and
querying).

## Why page-aware chunks?

Two reasons. First, citations: a citation that just says "somewhere in this
90-page PDF" is nearly useless to a researcher who needs to verify a claim;
"page 4" lets them check it in seconds. Second, retrieval quality: chunking
within a single page (rather than across arbitrary character counts spanning
multiple pages) keeps each chunk topically coherent, since PDF pages are
usually a reasonable unit of "one part of the argument."

## How is hallucination reduced?

Three separate mechanisms, not one:
- **Structural no-evidence protection** (below) - the LLM is never given
  the chance to answer when there's no supporting evidence.
- **Grounded prompting** - the system prompt explicitly restricts the model
  to the numbered sources it was given.
- **Citations built from retrieval, not generation** - even if the model's
  prose overstated something, the citations attached to the answer are
  always real chunks with real page numbers, so an answer can be checked
  against its stated evidence.

None of these make hallucination structurally impossible for the *prose* of
a grounded answer (that would require output-level fact verification, which
this project does not implement) - but they remove the two cheapest paths
to a fabricated answer: no-evidence guessing and fabricated sources.

## How are citations generated?

Citations are a side effect of retrieval, not of generation. When chunks
survive the similarity threshold, `citation.build_sources()` turns each one
into a `{document_id, filename, page, score, evidence}` object *before* the
LLM is called. The LLM's job is only to write prose that references source
numbers already tied to that pre-built list; it cannot introduce a citation
that doesn't correspond to a chunk retrieval actually found.

## What happens when evidence is missing?

`chat_service.answer()` checks whether retrieval returned anything above
`SIMILARITY_THRESHOLD` *before* it ever constructs a prompt or calls the
LLM. If nothing survived, it returns a fixed response
(`grounded: false, sources: [], answer: "I couldn't find sufficient
evidence..."`) directly - the LLM is never invoked for that request. This
is a code-level branch, not a prompt instruction the model could ignore or
be talked around.
