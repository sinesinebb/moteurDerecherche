# models/kafka_events.py
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    SEARCH_PERFORMED = "search_performed"
    SEARCH_RESULTS_CLICKED = "search_results_clicked"
    DOMAIN_VALIDATED = "domain_validated"
    DOCUMENT_CRAWLED = "document_crawled"
    DOCUMENT_INDEXED = "document_indexed"
    RANKING_UPDATED = "ranking_updated"
    USER_ACTION = "user_action"
    SYSTEM_METRIC = "system_metric"

class KafkaEvent(BaseModel):
    """Modèle de base pour tous les événements Kafka"""
    event_type: EventType
    timestamp: datetime
    service: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = {}

class SearchEvent(KafkaEvent):
    """Événement de recherche"""
    event_type: EventType = EventType.SEARCH_PERFORMED
    data: Dict[str, Any] = {
        "query": str,
        "user_id": Optional[str],
        "results_count": int,
        "processing_time": float,
        "domain_category": str,
        "filters": Dict[str, Any]
    }

class ClickEvent(KafkaEvent):
    """Événement de clic sur un résultat"""
    event_type: EventType = EventType.SEARCH_RESULTS_CLICKED
    data: Dict[str, Any] = {
        "user_id": Optional[str],
        "query": str,
        "doc_id": str,
        "rank": int,
        "session_id": str,
        "click_duration": Optional[float]
    }

class DomainValidationEvent(KafkaEvent):
    """Événement de validation de domaine"""
    event_type: EventType = EventType.DOMAIN_VALIDATED
    data: Dict[str, Any] = {
        "query": str,
        "is_informatics_domain": bool,
        "confidence_score": float,
        "category": str,
        "validation_time": float
    }

class DocumentCrawledEvent(KafkaEvent):
    """Événement de document crawlé"""
    event_type: EventType = EventType.DOCUMENT_CRAWLED
    data: Dict[str, Any] = {
        "doc_id": str,
        "url": str,
        "domain": str,
        "content_type": str,
        "crawl_duration": float,
        "content_size": int,
        "crawler_id": str
    }

class DocumentIndexedEvent(KafkaEvent):
    """Événement de document indexé"""
    event_type: EventType = EventType.DOCUMENT_INDEXED
    data: Dict[str, Any] = {
        "doc_id": str,
        "indexing_time": float,
        "document_size": int,
        "keywords_count": int,
        "indexer_id": str
    }

class RankingUpdateEvent(KafkaEvent):
    """Événement de mise à jour du ranking"""
    event_type: EventType = EventType.RANKING_UPDATED
    data: Dict[str, Any] = {
        "update_type": str,  # "page_rank", "relevance", "freshness"
        "documents_updated": int,
        "processing_time": float,
        "algorithm_version": str
    }

class UserActionEvent(KafkaEvent):
    """Événement d'action utilisateur"""
    event_type: EventType = EventType.USER_ACTION
    data: Dict[str, Any] = {
        "user_id": str,
        "action_type": str,  # "login", "logout", "preference_update"
        "details": Dict[str, Any],
        "user_agent": Optional[str],
        "ip_address": Optional[str]
    }