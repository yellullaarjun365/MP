from uuid import UUID

from fastapi import Header, HTTPException

from app.core.config import settings


DEV_USER_ID = UUID("11111111-1111-1111-1111-111111111111")


def get_current_user_id(
    x_dev_user_id: UUID | None = Header(
        default=None,
        alias="X-Dev-User-ID",
    ),
) -> UUID:
    """
    Temporary development authentication.

    This will be replaced by the Google OAuth/session layer
    once real authentication is implemented.
    """
    if not settings.debug:
        raise HTTPException(
            status_code=500,
            detail="Development authentication is disabled.",
        )

    if x_dev_user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Missing X-Dev-User-ID header.",
        )

    return x_dev_user_id
