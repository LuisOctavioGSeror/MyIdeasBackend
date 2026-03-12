# app/core/config.py
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação (carregadas de variáveis de ambiente / .env).

    - Pydantic v2 + pydantic-settings
    - extra="ignore": ignora envs que não estiverem mapeadas (evita ValidationError)
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- App / HTTP ---
    api_key: Optional[str] = Field(default=None, alias="API_KEY")  # x-api-key para /chat
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")   # CSV de origens

    # --- MCP ---
    # Se o MCP estiver no mesmo FastAPI, pode ser "http://localhost:8000/mcp".
    # Em produção (Railway), você pode sobrescrever por env.
    mcp_url: str = Field(default="http://localhost:8000/mcp", alias="MCP_URL")

    # --- Provedores LLM ---
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")  # openai | anthropic | groq

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-7-sonnet-latest", alias="ANTHROPIC_MODEL")

    # Groq (compatível com API estilo OpenAI)
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    groq_model: Optional[str] = Field(default=None, alias="GROQ_MODEL")

    # --- Storage (imagens) ---
    storage_provider: str = Field(default="s3", alias="STORAGE_PROVIDER")  # s3 (S3, R2, etc.)
    s3_bucket: Optional[str] = Field(default=None, alias="S3_BUCKET")
    s3_region: Optional[str] = Field(default=None, alias="S3_REGION")
    s3_endpoint_url: Optional[str] = Field(default=None, alias="S3_ENDPOINT_URL")
    s3_access_key_id: Optional[str] = Field(default=None, alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: Optional[str] = Field(default=None, alias="S3_SECRET_ACCESS_KEY")
    # URL base pública opcional (ex.: https://my-bucket.s3.amazonaws.com)
    s3_public_base_url: Optional[str] = Field(default=None, alias="S3_PUBLIC_BASE_URL")

    # --- Banco de dados (se você usa Postgres) ---
    postgres_user: Optional[str] = Field(default=None, alias="POSTGRES_USER")
    postgres_password: Optional[str] = Field(default=None, alias="POSTGRES_PASSWORD")
    postgres_db: Optional[str] = Field(default=None, alias="POSTGRES_DB")
    postgres_host: Optional[str] = Field(default=None, alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    # PgAdmin (opcional, caso use em dev/intra)
    pgadmin_default_email: Optional[str] = Field(default=None, alias="PGADMIN_DEFAULT_EMAIL")
    pgadmin_default_password: Optional[str] = Field(default=None, alias="PGADMIN_DEFAULT_PASSWORD")

    # --- Auth/JWT (se usado no seu projeto) ---
    secret_key: Optional[str] = Field(default=None, alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # --- Ambiente ---
    environment: str = Field(default="local", alias="ENVIRONMENT")

    # --- Helpers computados ---
    @property
    def cors_origins_list(self) -> list[str]:
        """Converte CORS_ORIGINS 'a,b,c' -> ['a','b','c'] (com trim)."""
        return [o.strip() for o in (self.cors_origins or "").split(",") if o.strip()]

    @property
    def database_url(self) -> Optional[str]:
        """Monta a URL do Postgres se todas as partes existirem."""
        if all([self.postgres_user, self.postgres_password, self.postgres_host, self.postgres_db]):
            return (
                f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        return None

    @property
    def railway_public_url(self) -> Optional[str]:
        """
        Tenta montar a URL pública no Railway, caso as envs padrão estejam disponíveis.
        Obs.: use apenas se precisar; geralmente o Railway já fornece o domínio público.
        """
        import os
        domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        if domain:
            return f"https://{domain}"
        return None


@lru_cache
def get_settings() -> Settings:
    return Settings()
