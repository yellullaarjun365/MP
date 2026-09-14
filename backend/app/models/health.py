import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class HealthEvent(Base):
    __tablename__ = "health_events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    pond_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "ponds.id",
            name="fk_health_pond_id_ponds",
        ),
        nullable=False,
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    mortality_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    symptoms: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    treatment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="manual",
    )

    __table_args__ = (
        Index(
            "ix_health_pond_observed_at",
            "pond_id",
            "observed_at",
        ),
    )
