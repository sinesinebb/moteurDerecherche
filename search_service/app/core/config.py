# app/core/config.py
from pydantic_settings import BaseSettings  # CORRECTION: utiliser pydantic_settings
from typing import List, Optional
from functools import lru_cache
import secrets
import logging

class Settings(BaseSettings):
    """Configuration de l'application avec pydantic-settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_SECRET_KEY: str = "temp-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Service URLs
    USER_SERVICE_URL: str = "http://user-service:8000"
    INDEXING_SERVICE_URL: str = "http://indexing-service:8000"
    PAGERANK_SERVICE_URL: str = "http://pagerank-service:8000"
    
    # Database & Cache
    ELASTICSEARCH_HOST: str = "elasticsearch"
    ELASTICSEARCH_PORT: int = 9200
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_ENABLED: bool = False
    
    # Performance
    SEARCH_TIMEOUT: int = 10
    MAX_RESULTS_PER_PAGE: int = 50
    CACHE_TTL: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Retourne les settings avec cache"""
    return Settings()

# Instance globale
settings = get_settings()