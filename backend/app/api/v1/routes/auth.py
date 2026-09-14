from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.auth.oauth import oauth
from app.core.config import settings
from app.db.session import get_db
from app.services.auth_service import find_or_create_google_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/google")
async def google_login(
    request: Request,
):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Google OAuth is not configured. "
                "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
            ),
        )

    google = oauth.create_client("google")

    return await google.authorize_redirect(
        request,
        settings.google_redirect_uri,
    )


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured.",
        )

    google = oauth.create_client("google")

    try:
        token = await google.authorize_access_token(request)

        print(
            "Google token received:",
            bool(token),
            "userinfo:",
            bool(token.get("userinfo")),
        )

        userinfo = token.get("userinfo")

        if not userinfo:
            raise HTTPException(
                status_code=401,
                detail="Google user information was not returned.",
            )

        subject = userinfo.get("sub")
        email = userinfo.get("email")
        email_verified = userinfo.get("email_verified", False)
        full_name = userinfo.get("name")

        print(
            "Google identity:",
            {
                "has_subject": bool(subject),
                "email": email,
                "email_verified": email_verified,
                "has_name": bool(full_name),
            },
        )

        if not subject:
            raise HTTPException(
                status_code=401,
                detail="Google account subject is missing.",
            )

        if not email:
            raise HTTPException(
                status_code=401,
                detail="Google account email is missing.",
            )

        if not email_verified:
            raise HTTPException(
                status_code=401,
                detail="Google email is not verified.",
            )

        user = find_or_create_google_user(
            db,
            subject=subject,
            email=email,
            full_name=full_name,
        )

        request.session["user_id"] = str(user.id)

        return RedirectResponse(
            url=settings.auth_success_redirect_url,
            status_code=303,
        )

    except HTTPException:
        raise

    except Exception as exc:
        print(
            "GOOGLE OAUTH CALLBACK ERROR:",
            type(exc).__name__,
            str(exc),
        )

        if settings.debug:
            raise HTTPException(
                status_code=500,
                detail=f"Google OAuth callback error: {type(exc).__name__}: {exc}",
            ) from exc

        raise HTTPException(
            status_code=401,
            detail="Google authentication failed.",
        ) from exc


@router.post("/logout")
async def logout(
    request: Request,
):
    request.session.clear()

    return {
        "status": "logged_out",
    }


@router.get("/config-status")
def auth_config_status():
    return {
        "google_configured": bool(
            settings.google_client_id
            and settings.google_client_secret
        ),
        "redirect_uri": settings.google_redirect_uri,
        "redirect_host": request_host(settings.google_redirect_uri),
    }


def request_host(url: str) -> str | None:
    try:
        from urllib.parse import urlparse

        return urlparse(url).hostname
    except Exception:
        return None
