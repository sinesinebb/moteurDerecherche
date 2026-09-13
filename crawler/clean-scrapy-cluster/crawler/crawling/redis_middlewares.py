# crawler/crawling/redis_middlewares.py
"""
Compat middleware shim pour éviter l'erreur
ModuleNotFoundError: No module named 'scrapy_redis.middlewares'
Implémente des middlewares très simples (pas d'effet secondaire),
suffisants pour que Scrapy charge les classes attendues.
"""

from typing import Iterable, Generator

class RedisSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        # on peut récupérer des settings si besoin plus tard
        return cls()

    def process_spider_input(self, response, spider):
        # rien à faire avant les callbacks
        return None

    def process_spider_output(self, response, result, spider) -> Generator:
        # passe-through des items/requests générés
        for r in result:
            yield r

    def process_spider_exception(self, response, exception, spider):
        # ne gère pas d'exception particulière pour l'instant
        return None

    def process_start_requests(self, start_requests, spider) -> Iterable:
        for req in start_requests:
            yield req


class RedisTimeoutMiddleware:
    def __init__(self, timeout=None):
        self.timeout = timeout

    @classmethod
    def from_crawler(cls, crawler):
        # on peut l'initialiser depuis les settings (DOWNLOAD_TIMEOUT etc.)
        return cls(timeout=crawler.settings.getint("DOWNLOAD_TIMEOUT", None))

    def process_request(self, request, spider):
        # pas de modification du request ; permet d'exister pour Scrapy
        return None
