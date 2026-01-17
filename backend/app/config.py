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
    
    @property # Converts a method into an attribute, fetching this attribute runs this function
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

# Create a single instance so it is only loaded once
settings = Settings()