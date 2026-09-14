import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class StockingRecord(Base):
    __tablename__ = "stocking_records"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    pond_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "ponds.id",
            name="fk_stocking_pond_id_ponds",
        ),
        nullable=False,
    )

    species_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "species.id",
            name="fk_stocking_species_id_species",
        ),
        nullable=False,
    )

    stocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    initial_average_weight_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="manual",
    )

    __table_args__ = (
        Index(
            "ix_stocking_pond_stocked_at",
            "pond_id",
            "stocked_at",
        ),
    )
