import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class GrowthRecord(Base):
    __tablename__ = "growth_records"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    pond_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "ponds.id",
            name="fk_growth_pond_id_ponds",
        ),
        nullable=False,
    )

    sampled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    average_weight_g: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    sample_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    estimated_biomass_kg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="manual",
    )

    __table_args__ = (
        Index(
            "ix_growth_pond_sampled_at",
            "pond_id",
            "sampled_at",
        ),
    )
