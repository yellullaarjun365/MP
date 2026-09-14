import uuid

from sqlalchemy import Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Pond(Base):
    __tablename__ = "ponds"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "farms.id",
            name="fk_ponds_farm_id_farms",
        ),
        nullable=False,
    )

    species_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "species.id",
            name="fk_ponds_species_id_species",
        ),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    area_m2: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    depth_m: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    culture_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    water_source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_ponds_farm_id",
            "farm_id",
        ),
        Index(
            "ix_ponds_species_id",
            "species_id",
        ),
        Index(
            "ix_ponds_farm_name",
            "farm_id",
            "name",
        ),
    )
