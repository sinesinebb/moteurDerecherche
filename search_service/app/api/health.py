# app/api/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "service": "search",
        "version": "1.0.0"
    }












# # api/health.py
# from fastapi import APIRouter, Depends
# from database.elasticsearch import es_client
# from database.redis import redis_client
# from services.analytics_service import analytics_service
# from core.config import settings
# import logging

# router = APIRouter()
# logger = logging.getLogger(__name__)

# @router.get("/")
# async def health_check():
#     """Health check basique"""
#     return {
#         "status": "healthy",
#         "service": "search-service",
#         "timestamp": datetime.utcnow().isoformat()
#     }

# @router.get("/detailed")
# async def detailed_health_check():
#     """Health check détaillé avec toutes les dépendances"""
#     checks = {}
    
#     # Vérifier Elasticsearch
#     try:
#         es = await es_client.get_client()
#         es_health = await es.cluster.health()
#         checks["elasticsearch"] = {
#             "status": "healthy",
#             "cluster_status": es_health.get('status'),
#             "number_of_nodes": es_health.get('number_of_nodes')
#         }
#     except Exception as e:
#         logger.error(f"Elasticsearch health check failed: {e}")
#         checks["elasticsearch"] = {
#             "status": "unhealthy",
#             "error": str(e)
#         }
    
#     # Vérifier Redis
#     try:
#         redis = await redis_client.get_client()
#         await redis.ping()
#         checks["redis"] = {
#             "status": "healthy"
#         }
#     except Exception as e:
#         logger.error(f"Redis health check failed: {e}")
#         checks["redis"] = {
#             "status": "unhealthy",
#             "error": str(e)
#         }
    
#     # Vérifier Kafka (via analytics service)
#     try:
#         # On suppose que si le service analytics est connecté, Kafka l'est aussi
#         if analytics_service.producer:
#             checks["kafka"] = {
#                 "status": "healthy"
#             }
#         else:
#             checks["kafka"] = {
#                 "status": "unhealthy",
#                 "error": "Kafka producer not initialized"
#             }
#     except Exception as e:
#         logger.error(f"Kafka health check failed: {e}")
#         checks["kafka"] = {
#             "status": "unhealthy",
#             "error": str(e)
#         }
    
#     # Déterminer le statut global
#     all_healthy = all(check["status"] == "healthy" for check in checks.values())
#     overall_status = "healthy" if all_healthy else "degraded"
    
#     return {
#         "status": overall_status,
#         "timestamp": datetime.utcnow().isoformat(),
#         "checks": checks
#     }

# @router.get("/ready")
# async def readiness_check():
#     """Readiness check pour Kubernetes"""
#     try:
#         # Vérifications essentielles
#         es = await es_client.get_client()
#         await es.cluster.health()
        
#         redis = await redis_client.get_client()
#         await redis.ping()
        
#         return {
#             "status": "ready",
#             "timestamp": datetime.utcnow().isoformat()
#         }
#     except Exception as e:
#         logger.error(f"Readiness check failed: {e}")
#         return {
#             "status": "not ready",
#             "error": str(e),
#             "timestamp": datetime.utcnow().isoformat()
#         }, 503