# database/elasticsearch.py
from elasticsearch import AsyncElasticsearch
from app.core.config import settings  # CORRECTION: ajouter app.
import logging

logger = logging.getLogger(__name__)

class ElasticsearchClient:
    def __init__(self):
        self.client = None
        self.index_name = "computer_science_docs"  # CORRECTION: valeur par défaut
    
    async def connect(self):
        """Établit la connexion à Elasticsearch"""
        try:
            # CORRECTION: utiliser les paramètres de settings
            es_host = getattr(settings, 'ELASTICSEARCH_HOST', 'elasticsearch')
            es_port = getattr(settings, 'ELASTICSEARCH_PORT', 9200)
            
            self.client = AsyncElasticsearch(
                hosts=[f"http://{es_host}:{es_port}"],
                timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
            # Vérifier la connexion
            if await self.client.ping():
                logger.info("✅ Connecté à Elasticsearch")
                
                # Vérifier si l'index existe, sinon le créer
                await self._ensure_index_exists()
            else:
                logger.error("❌ Impossible de se connecter à Elasticsearch")
        except Exception as e:
            logger.error(f"❌ Erreur de connexion Elasticsearch: {e}")
            # Ne pas lever l'exception pour permettre le démarrage
            logger.warning("Elasticsearch non disponible, mais l'application continue")
    
    async def _ensure_index_exists(self):
        """S'assure que l'index existe"""
        try:
            if not await self.client.indices.exists(index=self.index_name):
                # Créer l'index avec mapping de base
                await self.client.indices.create(
                    index=self.index_name,
                    body={
                        "settings": {
                            "number_of_shards": 1,
                            "number_of_replicas": 0
                        },
                        "mappings": {
                            "properties": {
                                "title": {"type": "text"},
                                "content": {"type": "text"},
                                "url": {"type": "keyword"},
                                "domain": {"type": "keyword"},
                                "timestamp": {"type": "date"}
                            }
                        }
                    }
                )
                logger.info(f"✅ Index '{self.index_name}' créé")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de créer l'index: {e}")
    
    async def close(self):
        """Ferme la connexion Elasticsearch"""
        if self.client:
            await self.client.close()
            logger.info("🔌 Connexion Elasticsearch fermée")
    
    async def get_client(self) -> AsyncElasticsearch:
        """Retourne le client Elasticsearch"""
        if not self.client:
            await self.connect()
        return self.client
    
    async def search(self, query: dict, index: str = None):
        """Recherche simplifiée dans Elasticsearch"""
        if not self.client:
            return {"hits": {"hits": []}}
        
        search_index = index or self.index_name
        
        try:
            response = await self.client.search(
                index=search_index,
                body=query
            )
            return response
        except Exception as e:
            logger.error(f"❌ Erreur de recherche Elasticsearch: {e}")
            return {"hits": {"hits": []}}

# Singleton pour l'application
es_client = ElasticsearchClient()