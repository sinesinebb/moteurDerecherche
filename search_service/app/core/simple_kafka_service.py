# services/simple_kafka_service.py
import json
import logging
from kafka import KafkaProducer
from core.kafka_config_simple import kafka_config

logger = logging.getLogger(__name__)

class SimpleKafkaService:
    """
    Service Kafka léger pour Search Service
    Seulement la production d'événements analytics
    """
    
    def __init__(self):
        self.producer = None
    
    async def connect(self):
        """Connexion simple au producer Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=kafka_config.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks=1,  # Pas besoin de haute durabilité pour analytics
                retries=2
            )
            logger.info("✅ Kafka Producer connecté (analytics seulement)")
        except Exception as e:
            logger.warning(f"⚠️ Kafka non disponible: {e}")
            self.producer = None
    
    def send_analytics_event(self, event_data: dict):
        """Envoie un événement analytics (non bloquant)"""
        if not self.producer:
            return
        
        try:
            self.producer.send(
                kafka_config.kafka_analytics_topic,
                value=event_data
            )
            # Pas de flush() - on accepte une perte potentielle d'événements
        except Exception as e:
            logger.warning(f"⚠️ Échec envoi événement analytics: {e}")
    
    async def close(self):
        """Ferme la connexion Kafka"""
        if self.producer:
            self.producer.close()

# Instance globale
kafka_service = SimpleKafkaService()