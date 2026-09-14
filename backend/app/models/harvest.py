import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class HarvestRecord(Base):
    __tablename__ = "harvest_records"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    pond_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "ponds.id",
            name="fk_harvest_pond_id_ponds",
        ),
        nullable=False,
    )

    harvested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    quantity_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    average_weight_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    survival_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    selling_price_per_kg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    buyer: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="manual",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_harvest_pond_harvested_at",
            "pond_id",
            "harvested_at",
        ),
    )
