# services/event_service.py
from typing import Dict, Any
from models.kafka_events import *
from services.kafka_service import kafka_service
from core.kafka_config import kafka_config
import logging

logger = logging.getLogger(__name__)

class EventService:
    """Service de gestion des événements Kafka"""
    
    def __init__(self):
        self.kafka_service = kafka_service
    
    async def initialize(self):
        """Initialise les consommateurs Kafka pour Search Service"""
        # Consumer pour les événements de crawling (si nécessaire)
        self.kafka_service.start_consumer(
            topic=kafka_config.kafka_crawler_topic,
            group_id=kafka_config.kafka_search_consumer_group,
            callback=self._handle_crawled_documents
        )
        
        # Consumer pour les mises à jour de ranking
        self.kafka_service.start_consumer(
            topic=kafka_config.kafka_ranking_updates_topic,
            group_id=kafka_config.kafka_search_consumer_group,
            callback=self._handle_ranking_updates
        )
        
        logger.info("✅ Consumers Kafka initialisés pour Search Service")
    
    async def publish_search_event(self, event_data: Dict[str, Any]):
        """Publie un événement de recherche"""
        event = SearchEvent(
            timestamp=datetime.utcnow(),
            service="search-service",
            data=event_data
        )
        
        self.kafka_service.produce_message(
            topic=kafka_config.kafka_search_topic,
            message=event.dict()
        )
    
    async def publish_click_event(self, event_data: Dict[str, Any]):
        """Publie un événement de clic"""
        event = ClickEvent(
            timestamp=datetime.utcnow(),
            service="search-service", 
            data=event_data
        )
        
        self.kafka_service.produce_message(
            topic=kafka_config.kafka_search_topic,
            message=event.dict()
        )
    
    async def publish_domain_validation_event(self, event_data: Dict[str, Any]):
        """Publie un événement de validation de domaine"""
        event = DomainValidationEvent(
            timestamp=datetime.utcnow(),
            service="search-service",
            data=event_data
        )
        
        self.kafka_service.produce_message(
            topic=kafka_config.kafka_domain_validation_topic,
            message=event.dict()
        )
    
    async def _handle_crawled_documents(self, message: Dict):
        """Traite les documents crawléss (pour mise à jour en temps réel)"""
        try:
            event = DocumentCrawledEvent(**message)
            logger.info(f"📥 Document crawlé reçu: {event.data['doc_id']}")
            
            # Ici, vous pourriez déclencher une pré-indexation
            # ou une mise à jour du cache en temps réel
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement document crawlé: {e}")
    
    async def _handle_ranking_updates(self, message: Dict):
        """Traite les mises à jour de ranking"""
        try:
            event = RankingUpdateEvent(**message)
            logger.info(f"🔄 Mise à jour ranking: {event.data['update_type']}")
            
            # Invalider le cache si nécessaire
            # ou recalculer certains scores
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement mise à jour ranking: {e}")

# Singleton
event_service = EventService()