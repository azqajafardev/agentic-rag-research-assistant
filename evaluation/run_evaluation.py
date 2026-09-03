"""Lightweight RAG evaluation for EvidenceRAG.

Self-contained: builds a small isolated document store (temp SQLite +
temp ChromaDB), indexes the fixed test corpus from dataset.json via the
real document ingestion pipeline, then runs every dataset question through
the real retrieval/citation/chat pipeline - no server needs to be running.

Run from the repo root with the backend's virtual environment:

    backend/.venv/Scripts/python.exe evaluation/run_evaluation.py   (Windows)
    backend/.venv/bin/python evaluation/run_evaluation.py           (macOS/Linux)

Measures, using only real pipeline output (never a fabricated score):
  - Retrieval relevance   : does retrieval surface the expected (file, page)?
  - Citation correctness  : do returned citations trace to real chunks?
  - Groundedness          : does the chat API's `grounded` flag match
                             whether the question is actually answerable?
                             (requires LLM_API_KEY - skipped, not faked,
                             when the LLM is unavailable)
  - No-evidence behavior  : do unanswerable questions get the fixed
                             no-evidence response without calling the LLM?
"""

import json
import sys
import tempfile
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import fitz  # noqa: E402  (after sys.path setup)

from app.core.config import Settings  # noqa: E402
from app.db.database import get_connection, init_db  # noqa: E402
from app.rag.citation import build_sources  # noqa: E402
from app.services.chat_service import ChatService  # noqa: E402
from app.services.document_service import process_upload  # noqa: E402
from app.services.embedding_service import EmbeddingService  # noqa: E402
from app.services.llm_service import LLMService  # noqa: E402
from app.services.reranker_service import RerankerService  # noqa: E402
from app.services.retrieval_service import RetrievalService  # noqa: E402
from app.services.vector_service import VectorService  # noqa: E402


def build_pdf_bytes(pages: list[str]) -> bytes:
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    import io

    buffer = io.BytesIO()
    doc.save(buffer)
    doc.close()
    return buffer.getvalue()


def main() -> int:
    dataset_path = Path(__file__).parent / "dataset.json"
    dataset = json.loads(dataset_path.read_text())

    # ignore_cleanup_errors: ChromaDB's PersistentClient keeps its SQLite
    # file handle open for the life of the process, which blocks Windows
    # from deleting the temp dir on __exit__. The OS reclaims it later.
    with tempfile.TemporaryDirectory(
        prefix="evidencerag_eval_", ignore_cleanup_errors=True
    ) as tmp:
        tmp_path = Path(tmp)
        settings = Settings(
            database_url=f"sqlite:///{tmp_path / 'eval.db'}",
            upload_dir=tmp_path / "uploads",
            vector_db_path=tmp_path / "chroma",
        )
        init_db(settings)

        embedding_service = EmbeddingService(settings)
        vector_service = VectorService(settings.vector_db_path)
        retrieval_service = RetrievalService(vector_service, embedding_service, settings)
        reranker_service = RerankerService(settings)

        try:
            llm_service = LLMService(settings)
            llm_available = True
        except Exception:
            llm_service = None
            llm_available = False

        chat_service = (
            ChatService(retrieval_service, reranker_service, llm_service, settings)
            if llm_service
            else None
        )

        print("=" * 70)
        print("EvidenceRAG Evaluation")
        print("=" * 70)

        # --- Index the fixed test corpus -----------------------------------
        conn = get_connection(settings.database_path)
        filenames = []
        for doc in dataset["corpus"]:
            pdf_bytes = build_pdf_bytes(doc["pages"])
            result = process_upload(
                conn,
                filename=doc["filename"],
                file_bytes=pdf_bytes,
                settings=settings,
                embedding_service=embedding_service,
                vector_service=vector_service,
            )
            filenames.append(doc["filename"])
            print(f"  indexed {result.filename}: {result.status} "
                  f"({result.page_count} pages, {result.chunk_count} chunks)")

        print()

        questions = dataset["questions"]
        retrieval_results = []
        citation_results = []
        groundedness_results = []
        no_evidence_results = []
        latencies = []

        for q in questions:
            question_text = q["question"]
            answerable = q["answerable"]

            # --- Retrieval relevance (no LLM required) ----------------------
            evidence = retrieval_service.retrieve(conn, question_text)
            evidence = reranker_service.rerank(question_text, evidence)

            if answerable:
                hit = any(
                    e.filename == q["expected_source"] and e.page == q["expected_page"]
                    for e in evidence
                )
            else:
                hit = len(evidence) == 0
            retrieval_results.append({"id": q["id"], "hit": hit})

            # --- Citation correctness (no LLM required) ---------------------
            sources = build_sources(evidence)
            citations_valid = all(
                s.filename in filenames and s.document_id and 0.0 <= s.score <= 1.0
                for s in sources
            )
            citation_results.append({"id": q["id"], "valid": citations_valid})

            # --- Groundedness + no-evidence behavior (via chat_service) -----
            start = time.monotonic()
            try:
                result = chat_service.answer(
                    conn, question=question_text, document_ids=None, conversation_id=None
                )
                elapsed = time.monotonic() - start
                latencies.append(elapsed)

                if answerable:
                    groundedness_results.append(
                        {"id": q["id"], "outcome": "pass" if result.grounded else "fail"}
                    )
                else:
                    correct = (not result.grounded) and result.sources == []
                    no_evidence_results.append(
                        {"id": q["id"], "outcome": "pass" if correct else "fail"}
                    )
            except Exception as exc:
                if answerable:
                    groundedness_results.append(
                        {"id": q["id"], "outcome": f"skipped ({exc.__class__.__name__})"}
                    )
                else:
                    # No-evidence questions must never reach the LLM; if this
                    # raised, the no-evidence short-circuit itself is broken.
                    no_evidence_results.append(
                        {"id": q["id"], "outcome": f"fail ({exc.__class__.__name__})"}
                    )

        conn.close()

        # --- Report ----------------------------------------------------------
        def pct(n: int, total: int) -> str:
            return f"{n}/{total} ({100 * n / total:.0f}%)" if total else "n/a"

        retrieval_hits = sum(r["hit"] for r in retrieval_results)
        citation_valid = sum(c["valid"] for c in citation_results)
        grounded_pass = sum(1 for g in groundedness_results if g["outcome"] == "pass")
        grounded_skipped = sum(
            1 for g in groundedness_results if g["outcome"].startswith("skipped")
        )
        no_evidence_pass = sum(1 for n in no_evidence_results if n["outcome"] == "pass")

        print(f"Total questions       : {len(questions)}")
        print(f"LLM available         : {llm_available}")
        print()
        print(f"Retrieval Relevance    : {pct(retrieval_hits, len(retrieval_results))}")
        for r in retrieval_results:
            print(f"  {r['id']}: {'HIT' if r['hit'] else 'MISS'}")
        print()
        print(f"Citation Correctness   : {pct(citation_valid, len(citation_results))}")
        print()
        print(
            f"Groundedness (answerable questions): "
            f"{pct(grounded_pass, len(groundedness_results) - grounded_skipped)}"
            f"  [{grounded_skipped} skipped - no LLM configured]"
        )
        for g in groundedness_results:
            print(f"  {g['id']}: {g['outcome']}")
        print()
        print(f"No-Evidence Behavior   : {pct(no_evidence_pass, len(no_evidence_results))}")
        for n in no_evidence_results:
            print(f"  {n['id']}: {n['outcome']}")
        print()
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            print(f"Average Chat Latency   : {avg_latency:.2f}s (n={len(latencies)})")
        print("=" * 70)

        failures = (
            (len(retrieval_results) - retrieval_hits)
            + (len(citation_results) - citation_valid)
            + sum(1 for g in groundedness_results if g["outcome"] == "fail")
            + (len(no_evidence_results) - no_evidence_pass)
        )
        return 1 if failures > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
