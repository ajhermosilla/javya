import logging
import secrets

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

_DEFAULT_SECRET = "generate_a_random_secret_key_here"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://javya:change_me_in_production@db:5432/javya"

    # Application
    debug: bool = False
    secret_key: str = _DEFAULT_SECRET

    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

if settings.secret_key == _DEFAULT_SECRET:
    settings.secret_key = secrets.token_hex(32)
    logger.warning(
        "SECRET_KEY not set — using a random key. Sessions will not survive restarts. "
        "Set SECRET_KEY in your environment for production."
    )
