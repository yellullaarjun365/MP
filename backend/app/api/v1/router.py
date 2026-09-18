from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    farms,
    onboarding,
    onboarding_status,
    me,
    operations,
    parameter_extraction,
    ponds,
    public_ai,
    species,
    voice,
)

from app.api.routes import prediction
from app.api.routes import model_registry
from app.api.routes import model_worker
from app.api.routes import fao_analytics
from app.api.routes import registry


api_router = APIRouter(
    prefix="/api/v1"
)

api_router.include_router(farms.router)
api_router.include_router(me.router)
api_router.include_router(ponds.router)
api_router.include_router(species.router)
api_router.include_router(operations.router)
api_router.include_router(onboarding.router)
api_router.include_router(onboarding_status.router)
api_router.include_router(auth.router)
api_router.include_router(parameter_extraction.router)
api_router.include_router(voice.router)
api_router.include_router(public_ai.router)
api_router.include_router(prediction.router)
api_router.include_router(fao_analytics.router)
api_router.include_router(registry.router)
api_router.include_router(model_registry.router)
api_router.include_router(model_worker.router)