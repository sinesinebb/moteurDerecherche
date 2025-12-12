from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from urllib.parse import urlparse

class Settings(BaseSettings):
    # Configuration Elasticsearch
    elasticsearch_url: str = Field(..., env="ELASTICSEARCH_URL")
    elasticsearch_index: str = Field("tech_docs", env="ELASTICSEARCH_INDEX")
    
    # Configuration Kafka
    kafka_bootstrap_servers: str = Field(..., env="KAFKA_BOOTSTRAP_SERVERS")
    kafka_topic_pagerank: str = Field("pagerank_updates", env="KAFKA_TOPIC_PAGERANK")
    
    # Configuration Redis - avec host et port séparés
    redis_url: str = Field(..., env="REDIS_URL")
    
    # Propriétés calculées pour redis_host et redis_port
    @property
    def redis_host(self):
        parsed = urlparse(self.redis_url)
        return parsed.hostname or "redis"
    
    @property
    def redis_port(self):
        parsed = urlparse(self.redis_url)
        return parsed.port or 6379
    
    @property
    def redis_db(self):
        parsed = urlparse(self.redis_url)
        if parsed.path:
            return int(parsed.path[1:]) if parsed.path[1:] else 0
        return 0
    
    # Configuration du service
    service_port: int = Field(8006, env="SERVICE_PORT")
    
    # Variables optionnelles
    log_level: Optional[str] = Field("INFO", env="LOG_LEVEL")
    env: Optional[str] = Field("development", env="ENV")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()