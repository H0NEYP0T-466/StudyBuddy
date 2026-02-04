from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "studybuddy"
    
    # AI Models
    gemini_api_key: Optional[str] = None
    longcat_api_key: Optional[str] = None
    github_token: Optional[str] = None
    
    # Server
    port: int = 8003
    host: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
