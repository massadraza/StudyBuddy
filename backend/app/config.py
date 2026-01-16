from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
 
    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int 
    
    # Database
    database_url: str 
    
    # CORS
    cors_origins: str 
    
    class Config:
        env_file = ".env"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()