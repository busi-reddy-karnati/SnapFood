from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    GEMINI_API_KEY: str = Field(...)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/snapfood"
    CORS_ORIGINS: list[str] = ["*"]

    # --- LLM abuse / cost controls -------------------------------------- #
    # One budget shared across all LLM endpoints (/intake, /suggestions),
    # keyed by device UUID (or client IP as fallback), plus a global ceiling
    # across all callers as an absolute wallet backstop. (Mirrors Fitnesswispr.)
    LLM_DAILY_LIMIT_PER_DEVICE: int = 100
    GLOBAL_LLM_DAILY_LIMIT: int = 5000
    LLM_RATE_WINDOW_SECONDS: int = 86400  # rolling 24h

    # Per-request input caps (reject before spending Gemini tokens).
    MAX_INTAKE_CHARS: int = 2000
    MAX_IMAGE_BYTES: int = 8 * 1024 * 1024  # 8 MB decoded upload

    # Per-call Gemini output caps. Keep generous: with JSON responses a
    # truncated output is invalid JSON, so these must fit real outputs.
    INTAKE_MAX_OUTPUT_TOKENS: int = 2048
    SUGGESTION_MAX_OUTPUT_TOKENS: int = 4096

    # --- Payload size limits (DB/memory abuse on non-LLM endpoints) ------ #
    MAX_REQUEST_BODY_BYTES: int = 12 * 1024 * 1024  # > the largest legit image body
    MAX_MEMBERS: int = 25
    MAX_PANTRY_ITEMS: int = 500
    MAX_GROCERY_ITEMS: int = 500

    # Sign in with Apple / sessions — dormant in v0 (device-UUID-first), kept
    # for the later sign-in phase.
    APPLE_BUNDLE_ID: str = "com.snapfood.app"
    APPLE_ISSUER: str = "https://appleid.apple.com"
    APPLE_JWKS_URL: str = "https://appleid.apple.com/auth/keys"

    JWT_SECRET: str = "dev-insecure-change-me-please-set-a-real-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 365


settings = Settings()
