"""
TriCare AI Backend Configuration

This module handles all configuration settings for the FastAPI application,
loading from environment variables with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

# Get the backend directory path
BACKEND_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "TriCare AI"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Azure OpenAI
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str = "gpt-4"
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_vision_deployment: str = "gpt-4-vision"
    
    # CORS
    allowed_origins: str = "http://localhost:3000"
    
    # File Upload
    max_file_size_mb: int = 10
    upload_dir: str = "./uploads"
    
    # ML Model
    model_path: str = "./app/models/weights/mobilenetv2_xray.pth"
    use_gpu: bool = False
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def cors_origins(self) -> list[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size to bytes."""
        return self.max_file_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Cached application settings
    """
    return Settings()
