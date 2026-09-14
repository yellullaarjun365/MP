from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine


app = FastAPI(
    title="AquaLife API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "AquaLife API",
        "version": "0.1.0",
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
