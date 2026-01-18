from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str

    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Database (PostgreSQL)
    database_url: str

    # pgvector connection (optional, defaults to database_url)
    pgvector_connection: Optional[str] = None

    # CORS
    cors_origins: str

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def vector_connection(self) -> str:
        """Return pgvector connection, defaulting to database_url if not set"""
        return self.pgvector_connection or self.database_url

# Create a single instance so it is only loaded once
settings = Settings()