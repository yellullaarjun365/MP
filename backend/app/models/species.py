import uuid

from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Species(Base):
    __tablename__ = "species"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    common_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    scientific_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    ponds: Mapped[list["Pond"]] = relationship(
        "Pond",
        back_populates="species",
        foreign_keys="Pond.species_id",
    )

    __table_args__ = (
        Index(
            "ix_species_common_name",
            "common_name",
            unique=True,
        ),
        Index(
            "ix_species_category",
            "category",
        ),
    )
