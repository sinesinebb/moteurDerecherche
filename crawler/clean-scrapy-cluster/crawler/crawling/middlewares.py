# crawling/middlewares.py
from scrapy import Request
from urllib.parse import urlparse

class DomainLimitMiddleware:
    """
    Intercepte chaque requête sortante juste avant son envoi.
    Si le domaine a atteint la limite de pages ou de score, la requête est rejetée.
    """
    def process_spider_output(self, response, result, spider):
        for element in result:
            if isinstance(element, Request):
                domain = urlparse(element.url).netloc
                if domain and hasattr(spider, 'should_follow_domain'):
                    if not spider.should_follow_domain(domain):
                        spider.logger.debug(
                            f"🚫 Requête rejetée (domaine {domain} saturé) : {element.url}"
                        )
                        # On ne yield pas la requête, elle est ignorée
                        continue
            yield element