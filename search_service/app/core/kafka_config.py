# core/kafka_config.py
from pydantic import BaseSettings
from typing import List, Dict

class KafkaConfig(BaseSettings):
    # Configuration Kafka
    kafka_bootstrap_servers: List[str] = ["kafka:9092"]
    
    # Topics
    kafka_search_topic: str = "search-events"
    kafka_crawler_topic: str = "crawled-data" 
    kafka_indexing_topic: str = "indexing-tasks"
    kafka_analytics_topic: str = "search-analytics"
    kafka_user_actions_topic: str = "user-actions"
    kafka_domain_validation_topic: str = "domain-validation"
    kafka_ranking_updates_topic: str = "ranking-updates"
    
    # Consumer Groups
    kafka_search_consumer_group: str = "search-service"
    kafka_indexing_consumer_group: str = "indexing-service"
    kafka_analytics_consumer_group: str = "analytics-service"
    
    # Configuration producer
    kafka_producer_config: Dict = {
        'acks': 'all',
        'retries': 3,
        'batch_size': 16384,
        'linger_ms': 1,
        'buffer_memory': 33554432,
    }
    
    # Configuration consumer
    kafka_consumer_config: Dict = {
        'auto_offset_reset': 'earliest',
        'enable_auto_commit': True,
        'auto_commit_interval_ms': 5000,
        'max_poll_records': 100,
    }

kafka_config = KafkaConfig()