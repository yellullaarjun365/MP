"""add onboarding status

Revision ID: 9c1361d467f4
Revises: d4791660f688
Create Date: 2026-09-14 20:35:30.711349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c1361d467f4"
down_revision: Union[str, Sequence[str], None] = "d4791660f688"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the column temporarily with a database default so
    # existing rows can be migrated safely.
    op.add_column(
        "users",
        sa.Column(
            "onboarding_status",
            sa.String(length=30),
            nullable=False,
            server_default="not_started",
        ),
    )

    # Existing users who already own at least one farm
    # have effectively completed the initial setup.
    op.execute(
        """
        UPDATE users
        SET onboarding_status = 'completed'
        WHERE EXISTS (
            SELECT 1
            FROM farms
            WHERE farms.owner_id = users.id
        )
        """
    )

    # Remove the database-level default after backfilling.
    # New users will be assigned the application-level default
    # from the SQLAlchemy model.
    op.alter_column(
        "users",
        "onboarding_status",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("users", "onboarding_status")
