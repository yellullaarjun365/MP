import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Pond(Base):
    __tablename__ = "ponds"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    area_m2: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    species: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
