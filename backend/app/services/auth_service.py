from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def find_or_create_google_user(
    db: Session,
    *,
    subject: str,
    email: str,
    full_name: str | None,
) -> User:

    # --------------------------------------------------------
    # Primary lookup: stable Google subject
    # --------------------------------------------------------

    user = db.scalar(
        select(User).where(
            User.auth_provider == "google",
            User.provider_subject == subject,
        )
    )

    if user is not None:
        return user


    # --------------------------------------------------------
    # Secondary lookup: existing account with same email
    #
    # Useful when a development account is converted to Google.
    # --------------------------------------------------------

    user = db.scalar(
        select(User).where(
            User.email == email,
        )
    )

    if user is not None:

        # Only link an existing development account.
        if user.auth_provider == "development":
            user.auth_provider = "google"
            user.provider_subject = subject

            if full_name and not user.full_name:
                user.full_name = full_name

            db.commit()
            db.refresh(user)

            return user

        raise ValueError(
            "An account with this email already exists "
            "with another authentication provider."
        )


    # --------------------------------------------------------
    # Create new AquaLife user
    # --------------------------------------------------------

    user = User(
        id=uuid4(),
        email=email,
        full_name=full_name,
        onboarding_status="not_started",
        auth_provider="google",
        provider_subject=subject,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
