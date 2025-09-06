import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application settings
    app_name: str = "AI Communication Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "sqlite:///./data/email_database.db"
    use_dataset: bool = True
    dataset_path: Optional[str] = "./data/Support_Emails_Dataset.csv"
    
    # Email service settings
    email_host: str = "smtp.gmail.com"
    email_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_use_tls: bool = True
    
    # IMAP settings
    imap_host: str = "imap.gmail.com"
    imap_port: int = 993
    imap_username: Optional[str] = None
    imap_password: Optional[str] = None
    imap_use_ssl: bool = True
    
    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 500
    openai_temperature: float = 0.7
    
    # Hugging Face settings
    hf_cache_dir: str = "./models"
    hf_use_auth_token: bool = False
    
    # Processing settings
    max_email_length: int = 10000
    batch_size: int = 10
    processing_delay: int = 5  # seconds
    
    # Support keywords for email filtering
    support_keywords: list = [
        "help", "support", "issue", "problem", "error", "bug", "broken",
        "not working", "can't", "cannot", "failed", "failure", "assistance",
        "question", "inquiry", "complaint", "feedback", "suggestion"
    ]
    
    # Security settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring settings
    enable_metrics: bool = True
    metrics_port: int = 8001
    
    # Cache settings
    redis_url: Optional[str] = None
    cache_ttl: int = 3600  # 1 hour
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

# Create global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "production":
    settings.debug = False
    settings.log_level = "WARNING"
elif os.getenv("ENVIRONMENT") == "development":
    settings.debug = True
    settings.log_level = "DEBUG"

# Load from environment variables if not set
if not settings.openai_api_key:
    settings.openai_api_key = os.getenv("OPENAI_API_KEY")

if not settings.email_username:
    settings.email_username = os.getenv("EMAIL_USERNAME")

if not settings.email_password:
    settings.email_password = os.getenv("EMAIL_PASSWORD")

if not settings.imap_username:
    settings.imap_username = os.getenv("IMAP_USERNAME")

if not settings.imap_password:
    settings.imap_password = os.getenv("IMAP_PASSWORD")

if not settings.secret_key or settings.secret_key == "your-secret-key-here":
    settings.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Dataset overrides
env_use_dataset = os.getenv("USE_DATASET")
if env_use_dataset is not None:
    settings.use_dataset = env_use_dataset.lower() in ["1", "true", "yes"]

if not settings.dataset_path:
    # Quote-aware path from env; if path has spaces, ensure it's not truncated
    settings.dataset_path = os.getenv("DATASET_PATH", "./data/Support_Emails_Dataset.csv")

# Validate required settings
def validate_settings():
    """Validate that all required settings are configured"""
    required_settings = [
        "openai_api_key",
        "email_username", 
        "email_password",
        "imap_username",
        "imap_password"
    ]
    
    missing_settings = []
    for setting in required_settings:
        if not getattr(settings, setting):
            missing_settings.append(setting)
    
    if missing_settings:
        print(f"Warning: Missing required settings: {missing_settings}")
        print("Please set these environment variables or update your .env file")
    
    return len(missing_settings) == 0

# Export settings
__all__ = ["settings", "validate_settings"]