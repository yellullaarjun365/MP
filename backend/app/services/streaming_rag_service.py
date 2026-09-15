from typing import Any, Iterator

from app.ai.ollama import provider
from app.services.rag_service import retrieve_knowledge


RAG_SYSTEM_PROMPT = """
You are Aqua AI, an evidence-grounded aquaculture assistant.

Use the retrieved evidence as the primary factual source.

Rules:
- Do not invent facts, measurements, ranges, thresholds, treatments,
  or recommendations not supported by the evidence.
- If the evidence is insufficient, say so.
- Cite important factual claims using [Source: filename, p. X].
- Do not claim access to private farm data unless it is explicitly provided.
- Keep the answer concise and practical.
""".strip()


def build_rag_context(
    question: str,
    limit: int = 3,
) -> tuple[str, list[dict[str, Any]]]:

    results = retrieve_knowledge(
        query=question,
        limit=limit,
    )

    context = "\n\n---\n\n".join(
        (
            f"[Source: {result['source_file']}, "
            f"p. {result['page']}]\n"
            f"{result['text'][:800]}"
        )
        for result in results
    )

    sources = [
        {
            "source_file": result["source_file"],
            "page": result["page"],
            "chunk_index": result["chunk_index"],
            "similarity": result["similarity"],
        }
        for result in results
    ]

    return context, sources


def stream_rag_answer(
    question: str,
    limit: int = 3,
) -> tuple[Iterator[str], list[dict[str, Any]]]:

    context, sources = build_rag_context(
        question,
        limit=limit,
    )

    messages = [
        {
            "role": "system",
            "content": RAG_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"Question:\n{question}\n\n"
                f"Retrieved evidence:\n{context}"
            ),
        },
    ]

    return (
        provider.chat_stream(
            messages,
            temperature=0.1,
            think=False,
        ),
        sources,
    )
