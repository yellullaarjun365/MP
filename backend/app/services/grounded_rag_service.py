from typing import Any

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
"""


def answer_with_rag(
    question: str,
    limit: int = 3,
) -> dict[str, Any]:

    results = retrieve_knowledge(
        query=question,
        limit=limit,
    )

    if not results:
        return {
            "answer": (
                "I could not find relevant evidence in the "
                "AquaLife knowledge base."
            ),
            "sources": [],
        }

    evidence = "\n\n---\n\n".join(
        (
            f"[Source: {result['source_file']}, "
            f"p. {result['page']}]\n"
            f"{result['text'][:800]}"
        )
        for result in results
    )

    answer = provider.chat(
        [
            {
                "role": "system",
                "content": RAG_SYSTEM_PROMPT.strip(),
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{question}\n\n"
                    f"Retrieved evidence:\n{evidence}"
                ),
            },
        ],
        temperature=0.1,
        think=False,
    )

    return {
        "answer": answer,
        "sources": [
            {
                "source_file": result["source_file"],
                "page": result["page"],
                "chunk_index": result["chunk_index"],
                "similarity": result["similarity"],
            }
            for result in results
        ],
    }
