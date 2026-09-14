from fastapi import APIRouter

from app.api.v1.routes import farms, ponds


api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(farms.router)
api_router.include_router(ponds.router)
