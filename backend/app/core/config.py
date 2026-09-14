from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AquaLife API"
    app_version: str = "0.1.0"
    debug: bool = True

    database_url: str = (
        "postgresql+psycopg://aqualife:aqualife_dev_pw"
        "@localhost:5433/aqualife"
    )

    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
