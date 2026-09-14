from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://aqualife:aqualife_dev_pw"
        "@localhost:5433/aqualife"
    )

    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
