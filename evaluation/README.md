# Evaluation

Lightweight, self-contained RAG evaluation. No server needs to be running -
it builds its own isolated SQLite + ChromaDB store, indexes the fixed test
corpus defined in `dataset.json`, and runs every question through the real
retrieval/citation/chat pipeline.

## Run

```bash
# Windows
backend\.venv\Scripts\python.exe evaluation\run_evaluation.py

# macOS/Linux
backend/.venv/bin/python evaluation/run_evaluation.py
```

## What it measures

- **Retrieval relevance** - does retrieval surface the expected (file, page) for answerable questions, and nothing for unanswerable ones? Doesn't require an LLM.
- **Citation correctness** - do returned citations trace back to real indexed chunks (real filename, valid score)? Doesn't require an LLM.
- **Groundedness** - does `/api/chat`'s `grounded` flag come back `true` for answerable questions? Requires `LLM_API_KEY` to be configured; reported as `skipped`, never faked, when it isn't.
- **No-evidence behavior** - do unanswerable questions get the fixed no-evidence response without ever calling the LLM? Doesn't require an LLM.

## Editing the dataset

`dataset.json` has two sections: `corpus` (a few short synthetic PDFs, generated at
run time - nothing to upload by hand) and `questions` (each with `answerable`,
and for answerable ones, the exact `expected_source`/`expected_page` retrieval
should surface). Keep new questions unambiguous relative to the corpus content,
or retrieval relevance will legitimately fail rather than reflect a real bug.
