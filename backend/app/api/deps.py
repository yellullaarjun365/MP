from uuid import UUID

from fastapi import Header, HTTPException
from starlette.requests import Request

from app.core.config import settings


DEV_USER_ID = UUID(
    "11111111-1111-1111-1111-111111111111"
)


def get_current_user_id(
    request: Request,
    x_dev_user_id: UUID | None = Header(
        default=None,
        alias="X-Dev-User-ID",
    ),
) -> UUID:

    # --------------------------------------------------------
    # Production/session authentication
    # --------------------------------------------------------

    session_user_id = request.session.get("user_id")

    if session_user_id:
        try:
            return UUID(str(session_user_id))
        except ValueError:
            request.session.clear()
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication session.",
            )


    # --------------------------------------------------------
    # Development authentication
    # --------------------------------------------------------

    if settings.debug and x_dev_user_id is not None:
        return x_dev_user_id


    raise HTTPException(
        status_code=401,
        detail="Authentication required.",
    )
