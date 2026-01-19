from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    # OpenAI (optional - users provide their own keys)
    openai_api_key: Optional[str] = None

    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # PostgreSQL Database
    database_url: str

    # pgvector connection (optional, defaults to database_url)
    pgvector_connection: Optional[str] = None

    # CORS
    cors_origins: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def vector_connection(self) -> str:
        """Return pgvector connection, defaulting to database_url if not set"""
        return self.pgvector_connection or self.database_url
    
    
# Create a single instance so it is only loaded once
settings = Settings()