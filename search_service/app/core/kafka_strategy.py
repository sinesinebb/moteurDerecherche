# core/kafka_strategy.py
from enum import Enum
from typing import Dict, List

class KafkaUsageStrategy:
    """
    Stratégie d'utilisation de Kafka par microservice
    """
    
    class ServiceRole(Enum):
        PRODUCER_ONLY = "producer_only"      # Produit des événements
        CONSUMER_ONLY = "consumer_only"      # Consomme des événements  
        BOTH = "both"                        # Les deux
        NONE = "none"                        # Pas de Kafka

    # Stratégie par microservice
    KAFKA_STRATEGY = {
        "search-service": {
            "role": ServiceRole.BOTH,
            "producer_topics": ["search-events", "click-events"],
            "consumer_topics": ["ranking-updates"],
            "rationale": "Événements analytics + mises à jour ranking"
        },
        "crawler-service": {
            "role": ServiceRole.PRODUCER_ONLY,
            "producer_topics": ["crawled-data"],
            "consumer_topics": [],
            "rationale": "Flux massif de données crawléss"
        },
        "indexing-service": {
            "role": ServiceRole.BOTH, 
            "producer_topics": ["indexing-events"],
            "consumer_topics": ["crawled-data"],
            "rationale": "Consommation données crawler + événements indexation"
        },
        "user-service": {
            "role": ServiceRole.PRODUCER_ONLY,
            "producer_topics": ["user-actions"],
            "consumer_topics": [],
            "rationale": "Événements utilisateur pour analytics"
        },
        "pagerank-service": {
            "role": ServiceRole.BOTH,
            "producer_topics": ["ranking-updates"], 
            "consumer_topics": ["indexing-events"],
            "rationale": "Recalcul basé sur nouveaux documents"
        },
        "admin-service": {
            "role": ServiceRole.CONSUMER_ONLY,
            "producer_topics": [],
            "consumer_topics": ["search-events", "user-actions"],
            "rationale": "Analytics et monitoring uniquement"
        },
        "chatbot-service": {
            "role": ServiceRole.NONE,
            "producer_topics": [],
            "consumer_topics": [],
            "rationale": "Temps réel - REST uniquement"
        }
    }