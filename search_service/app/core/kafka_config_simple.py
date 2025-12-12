# core/kafka_config_simple.py
from pydantic import BaseSettings
from typing import List

class SimpleKafkaConfig(BaseSettings):
    """Configuration Kafka simplifiée et ciblée"""
    
    # Serveurs Kafka
    kafka_bootstrap_servers: List[str] = ["kafka:9092"]
    
    # Topics essentiels uniquement
    kafka_crawled_topic: str = "crawled-data"
    kafka_ranking_topic: str = "ranking-updates" 
    kafka_analytics_topic: str = "search-analytics"
    
    # Consumer groups
    kafka_indexing_group: str = "indexing-service"
    kafka_pagerank_group: str = "pagerank-service"
    kafka_admin_group: str = "admin-service"
    
    class Config:
        env_file = ".env"

kafka_config = SimpleKafkaConfig()