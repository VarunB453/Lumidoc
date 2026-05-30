"""Application configuration via Pydantic BaseSettings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ----- App -----
    APP_ENV: Literal["development", "staging", "production", "test"] = "development"
    APP_NAME: str = "Lumidoc"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    SECRET_KEY: str = "change-me"

    FRONTEND_ORIGIN: str = "http://localhost:3000"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    # ----- JWT -----
    JWT_ALGORITHM: str = "RS256"
    JWT_PRIVATE_KEY_PATH: str = "./keys/private.pem"
    JWT_PUBLIC_KEY_PATH: str = "./keys/public.pem"
    ACCESS_TOKEN_TTL_MINUTES: int = 15
    REFRESH_TOKEN_TTL_DAYS: int = 7
    JWT_ISSUER: str = "lumidoc"
    JWT_AUDIENCE: str = "lumidoc-api"

    # ----- Mongo -----
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "lumidoc"

    # ----- Redis -----
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_DB: int = 1
    REDIS_RATELIMIT_DB: int = 2

    # ----- S3 -----
    USE_LOCAL_STORAGE: bool = True
    LOCAL_STORAGE_PATH: str = "./storage"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "lumidoc-files"
    S3_PRESIGNED_URL_TTL: int = 900
    MAX_UPLOAD_SIZE_MB: int = 500

    # ----- OpenRouter -----
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_APP_NAME: str = "Lumidoc"
    OPENROUTER_SITE_URL: str = "http://localhost:5173"
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini"
    OPENROUTER_EMBEDDING_MODEL: str = "openai/text-embedding-3-small"
    OPENROUTER_TEMPERATURE: float = 0.2
    OPENROUTER_MAX_TOKENS: int = 2048
    OPENROUTER_EMBEDDING_TIMEOUT_SECONDS: float = 30.0
    LLM_GENERATION_TIMEOUT_SECONDS: float = 60.0

    # ----- OpenAI (Whisper only) -----
    OPENAI_API_KEY: str = ""
    OPENAI_WHISPER_MODEL: str = "whisper-1"
    WHISPER_TIMEOUT_SECONDS: float = 60.0

    # ----- Vector store -----
    VECTOR_BACKEND: Literal["faiss", "pinecone"] = "faiss"
    FAISS_INDEX_DIR: str = "./storage/faiss"
    USE_PINECONE: bool = False
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east-1-aws"
    PINECONE_INDEX_NAME: str = "lumidoc"
    EMBEDDING_DIM: int = 1536

    # ----- Google OAuth -----
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    GOOGLE_FRONTEND_REDIRECT: str = "http://localhost:5173/auth/callback"

    # ----- Rate limiting -----
    RATE_LIMIT_PER_IP: int = 100
    RATE_LIMIT_PER_USER: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ----- Celery -----
    CELERY_BROKER_URL: str = "redis://localhost:6379/3"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/4"
    CELERY_CONCURRENCY: int = 4

    # ----- Logging -----
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = True

    @field_validator("ALLOWED_HOSTS")
    @classmethod
    def _validate_hosts(cls, v: str) -> str:
        return v or "localhost"

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [h.strip() for h in self.ALLOWED_HOSTS.split(",") if h.strip()]

    @property
    def cors_origins(self) -> list[str]:
        # FRONTEND_ORIGIN can be a comma-separated list (multiple deployed origins).
        origins = [o.strip() for o in self.FRONTEND_ORIGIN.split(",") if o.strip()]
        if self.APP_ENV == "development":
            origins.extend(
                [
                    "http://localhost:3000",
                    "http://localhost:5173",
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:5173",
                ]
            )
        return list(dict.fromkeys(origins))  # de-dupe but preserve order

    @property
    def api_origin(self) -> str:
        parsed = urlparse(self.GOOGLE_REDIRECT_URI)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
        return "http://localhost:8000"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_test(self) -> bool:
        return self.APP_ENV == "test"

    def load_jwt_keys(self) -> tuple[str, str]:
        """Load private + public PEM keys from disk (lazy)."""
        priv = Path(self.JWT_PRIVATE_KEY_PATH)
        pub = Path(self.JWT_PUBLIC_KEY_PATH)
        if not priv.exists() or not pub.exists():
            if self.APP_ENV not in {"development", "test"}:
                raise RuntimeError(
                    "JWT key files are required outside development/test."
                )
            # Auto-generate ephemeral keys in dev/test so tests run without setup.
            self._generate_ephemeral_keys(priv, pub)
        return priv.read_text(), pub.read_text()

    @staticmethod
    def _generate_ephemeral_keys(priv_path: Path, pub_path: Path) -> None:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        priv_path.parent.mkdir(parents=True, exist_ok=True)
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        priv_path.write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        pub_path.write_bytes(
            key.public_key().public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings singleton."""
    return Settings()


settings = get_settings()
