import uuid

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    onboarding_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="not_started",
    )

    auth_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="development",
    )

    provider_subject: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    farms: Mapped[list["Farm"]] = relationship(
        "Farm",
        back_populates="owner",
    )

    __table_args__ = (
        Index(
            "ix_users_auth_provider_subject",
            "auth_provider",
            "provider_subject",
            unique=True,
        ),
    )
