# api/dependencies.py
from fastapi import Depends
from services.search_engine import SearchEngine
from services.domain_validator import DomainValidator
from services.ranking_service import RankingService
from services.nlp_processor import NLPProcessor
from services.cache_service import SearchCache
from services.user_client import UserServiceClient
from services.indexing_client import IndexingServiceClient
from services.pagerank_client import PageRankClient
from services.chatbot_client import ChatbotServiceClient
from services.admin_client import AdminServiceClient
from database.elasticsearch import es_client
from database.redis import redis_client
from core.config import settings

async def get_search_engine() -> SearchEngine:
    """Dépendance pour le moteur de recherche"""
    es = await es_client.get_client()
    return SearchEngine(es)

async def get_domain_validator() -> DomainValidator:
    """Dépendance pour le validateur de domaine"""
    return DomainValidator()

async def get_ranking_service() -> RankingService:
    """Dépendance pour le service de ranking"""
    return RankingService()

async def get_nlp_processor() -> NLPProcessor:
    """Dépendance pour le processeur NLP"""
    return NLPProcessor()

async def get_cache_service() -> SearchCache:
    """Dépendance pour le service de cache"""
    redis = await redis_client.get_client()
    return SearchCache(redis)

async def get_user_client() -> UserServiceClient:
    """Dépendance pour le client User Service"""
    return UserServiceClient(settings.user_service_url)

async def get_indexing_client() -> IndexingServiceClient:
    """Dépendance pour le client Indexing Service"""
    return IndexingServiceClient(settings.indexing_service_url)

async def get_pagerank_client() -> PageRankClient:
    """Dépendance pour le client PageRank Service"""
    return PageRankClient(settings.pagerank_service_url)

async def get_chatbot_client() -> ChatbotServiceClient:
    """Dépendance pour le client Chatbot Service"""
    return ChatbotServiceClient(settings.chatbot_service_url)

async def get_admin_client() -> AdminServiceClient:
    """Dépendance pour le client Admin Service"""
    return AdminServiceClient(settings.admin_service_url)