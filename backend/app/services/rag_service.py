from typing import Any

import httpx
from sqlalchemy import create_engine, text

from app.core.config import settings


EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_EMBED_URL = "http://127.0.0.1:11434/api/embed"


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)


def embed_query(query: str) -> list[float]:
    response = httpx.post(
        OLLAMA_EMBED_URL,
        json={
            "model": EMBEDDING_MODEL,
            "input": query,
        },
        timeout=120,
    )

    response.raise_for_status()

    embedding = response.json()["embeddings"][0]

    if len(embedding) != 768:
        raise ValueError(
            f"Expected 768-dimensional embedding, got {len(embedding)}"
        )

    return embedding


def retrieve_knowledge(
    query: str,
    limit: int = 5,
    min_similarity: float = 0.0,
) -> list[dict[str, Any]]:

    embedding = embed_query(query)

    statement = text(
        """
        SELECT
            source_file,
            page,
            chunk_index,
            text,
            1 - (
                embedding <=> CAST(:embedding AS vector)
            ) AS similarity
        FROM knowledge_chunks
        WHERE 1 - (
            embedding <=> CAST(:embedding AS vector)
        ) >= :min_similarity
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
        """
    )

    with engine.connect() as db:
        rows = db.execute(
            statement,
            {
                "embedding": str(embedding),
                "min_similarity": min_similarity,
                "limit": limit,
            },
        ).mappings().all()

    return [
        {
            "source_file": row["source_file"],
            "page": row["page"],
            "chunk_index": row["chunk_index"],
            "text": row["text"],
            "similarity": float(row["similarity"]),
        }
        for row in rows
    ]
