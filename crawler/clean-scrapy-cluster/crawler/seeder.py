import logging
import json
from redis import Redis
from redis.exceptions import ConnectionError

logger = logging.getLogger(__name__)

class SeedHandler(object):
    """
    Gestionnaire de seeds (URLs initiales) pour le crawler.
    """

    def __init__(self, redis_conn, seed_key='scrapy-cluster:seeds'):
        self.redis_conn = redis_conn
        self.seed_key = seed_key

    def add_seed(self, url, metadata=None, domain=None):
        """Ajoute une seed avec métadonnées."""
        try:
            seed_data = {
                'url': url,
                'meta': metadata or {},
                'domain': domain or self._extract_domain(url)
            }
            serialized = json.dumps(seed_data)
            self.redis_conn.sadd(self.seed_key, serialized)
            logger.info(f"Seed ajoutée : {url}")
            return True
        except ConnectionError as e:
            logger.error(f"Erreur Redis : {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur d'ajout : {e}")
            return False

    def _extract_domain(self, url):
        """Extrait le domaine d'une URL."""
        return url.split('//')[-1].split('/')[0].split(':')[0]

    def get_all_seeds(self):
        """Récupère toutes les seeds."""
        try:
            seeds = self.redis_conn.smembers(self.seed_key)
            return [json.loads(s) for s in seeds]
        except Exception as e:
            logger.error(f"Erreur de lecture : {e}")
            return []

    def clear_seeds(self):
        """Supprime toutes les seeds."""
        try:
            self.redis_conn.delete(self.seed_key)
            return True
        except Exception as e:
            logger.error(f"Erreur de suppression : {e}")
            return False