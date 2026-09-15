from alembic import op


revision = "rag_hnsw_001"
down_revision = "44e09637deab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS
        ix_knowledge_chunks_embedding_hnsw
        ON knowledge_chunks
        USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS
        ix_knowledge_chunks_embedding_hnsw
        """
    )
