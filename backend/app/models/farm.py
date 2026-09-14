import uuid

from sqlalchemy import Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "users.id",
            name="fk_farms_owner_id_users",
        ),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    farm_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    total_area_m2: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    water_source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="farms",
        foreign_keys=[owner_id],
    )

    ponds: Mapped[list["Pond"]] = relationship(
        "Pond",
        back_populates="farm",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_farms_owner_id",
            "owner_id",
        ),
        Index(
            "ix_farms_owner_name",
            "owner_id",
            "name",
        ),
    )
