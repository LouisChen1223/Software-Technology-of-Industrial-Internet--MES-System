from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./mes.db"
    
    # API Settings
    api_version: str = "v1"
    api_prefix: str = "/api/v1"
    project_name: str = "MES System"
    
    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
