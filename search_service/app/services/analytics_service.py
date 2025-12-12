# services/analytics_service.py
import asyncio
from typing import Dict, List
from datetime import datetime
import json
from kafka import KafkaProducer
from core.config import settings

class AnalyticsService:
    def __init__(self):
        self.producer = None
        self.search_topic = settings.kafka_search_topic
    
    async def connect(self):
        """Établit la connexion à Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3
            )
            print("✅ Connecté à Kafka pour l'analytics")
        except Exception as e:
            print(f"❌ Erreur de connexion Kafka: {e}")
    
    async def track_search_event(self, event_data: Dict):
        """Track un événement de recherche"""
        if not self.producer:
            await self.connect()
        
        event = {
            'event_type': 'search',
            'timestamp': datetime.utcnow().isoformat(),
            'data': event_data
        }
        
        try:
            self.producer.send(self.search_topic, event)
            self.producer.flush()
        except Exception as e:
            print(f"Error sending search event to Kafka: {e}")
    
    async def track_click_event(self, user_id: str, doc_id: str, query: str, rank: int):
        """Track un clic sur un résultat"""
        event_data = {
            'user_id': user_id,
            'doc_id': doc_id,
            'query': query,
            'rank': rank,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.track_search_event({
            'event_type': 'click',
            **event_data
        })
    
    async def track_search_session(self, user_id: str, query: str, results_count: int, processing_time: float):
        """Track une session de recherche complète"""
        await self.track_search_event({
            'event_type': 'search_session',
            'user_id': user_id,
            'query': query,
            'results_count': results_count,
            'processing_time': processing_time,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def close(self):
        """Ferme la connexion Kafka"""
        if self.producer:
            self.producer.close()

# Singleton
analytics_service = AnalyticsService()