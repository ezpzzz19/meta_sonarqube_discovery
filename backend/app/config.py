"""
Application configuration using Pydantic settings.
All settings are loaded from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from os import getenv


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database
    database_url: str = getenv("DATABASE_URL", "postgresql://localhost:5432/sonarqube_codex")
    
    # SonarQube
    sonarqube_url: str
    sonarqube_token: str
    sonarqube_project_key: str
    
    # GitHub
    github_token: str
    github_repo_owner: str
    github_repo_name: str
    github_default_branch: str = "main"
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4"
    
    # Fixer Service
    auto_fix: bool = False
    poll_interval_seconds: int = 60
    
    # API
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    @property
    def github_repo_full_name(self) -> str:
        """Return full GitHub repository name."""
        return f"{self.github_repo_owner}/{self.github_repo_name}"


# Global settings instance
settings = Settings()