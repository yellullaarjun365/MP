from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AquaLife API"
    app_version: str = "0.1.0"
    debug: bool = True

    database_url: str = (
        "postgresql+psycopg://aqualife:aqualife_dev_pw"
        "@localhost:5433/aqualife"
    )

    redis_url: str = "redis://localhost:6379/0"

    session_secret_key: str = (
        "aqualife-local-development-secret-change-me"
    )

    google_client_id: str = ""
    google_client_secret: str = ""

    google_redirect_uri: str = (
        "http://127.0.0.1:8000/auth/google/callback"
    )

    auth_success_redirect_url: str = (
        "http://127.0.0.1:8000/docs"
    )


settings = Settings()
