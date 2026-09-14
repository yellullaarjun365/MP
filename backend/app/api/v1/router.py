from fastapi import APIRouter

from app.api.v1.routes import (
    farms,
    onboarding,
    onboarding_status,
    operations,
    ponds,
    public_ai,
    species,
    auth,
)

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(farms.router)
api_router.include_router(ponds.router)
api_router.include_router(species.router)
api_router.include_router(operations.router)
api_router.include_router(onboarding.router)
api_router.include_router(onboarding_status.router)
api_router.include_router(auth.router)
api_router.include_router(public_ai.router)
