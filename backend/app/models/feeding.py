import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class FeedingRecord(Base):
    __tablename__ = "feeding_records"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    pond_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "ponds.id",
            name="fk_feeding_pond_id_ponds",
        ),
        nullable=False,
    )

    feed_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    quantity_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    fed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="manual",
    )

    __table_args__ = (
        Index(
            "ix_feeding_pond_fed_at",
            "pond_id",
            "fed_at",
        ),
    )
