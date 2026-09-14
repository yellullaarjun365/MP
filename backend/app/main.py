from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/health/db")
def database_health():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    return {
        "status": "healthy",
        "database": "connected",
        "test_query": value,
    }
