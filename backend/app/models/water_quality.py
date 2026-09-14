import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class WaterQualityMeasurement(Base):
    __tablename__ = "water_quality_measurements"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    pond_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "ponds.id",
            name="fk_water_quality_pond_id_ponds",
        ),
        nullable=False,
    )

    parameter: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    measured_at: Mapped[datetime] = mapped_column(
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
            "ix_water_quality_pond_measured_at",
            "pond_id",
            "measured_at",
        ),
    )
