"""add auth provider identity

Revision ID: 90c8f00ff41c
Revises: 9c1361d467f4
Create Date: 2026-09-14 20:40:26.658824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "90c8f00ff41c"
down_revision: Union[str, Sequence[str], None] = "9c1361d467f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add auth_provider temporarily with a server default so
    # existing users can be migrated safely.
    op.add_column(
        "users",
        sa.Column(
            "auth_provider",
            sa.String(length=50),
            nullable=False,
            server_default="development",
        ),
    )

    # Existing development accounts do not have a real
    # external provider subject yet.
    op.add_column(
        "users",
        sa.Column(
            "provider_subject",
            sa.String(length=255),
            nullable=True,
        ),
    )

    # Remove the temporary database default.
    # New users will receive the application-level default
    # from the SQLAlchemy model.
    op.alter_column(
        "users",
        "auth_provider",
        server_default=None,
    )

    # The provider + subject pair uniquely identifies an
    # externally authenticated identity.
    op.create_index(
        "ix_users_auth_provider_subject",
        "users",
        ["auth_provider", "provider_subject"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_users_auth_provider_subject",
        table_name="users",
    )

    op.drop_column(
        "users",
        "provider_subject",
    )

    op.drop_column(
        "users",
        "auth_provider",
    )
