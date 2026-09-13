#!/usr/bin/env python
"""
Le “runner” principal du service crawler.  
Il :
  1) Charge la configuration JSON
  2) Initialise le logging
  3) Démarre un KafkaConsumer (écoute sc.crawl.request)
  4) À chaque message reçu : 
       - pousse l’URL dans Redis (clé sc:start_urls)
       - déclenche scrapy via CrawlerProcess
"""

import json
import logging
import signal
import sys
from kafka import KafkaConsumer
from redis import Redis
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# version Docker, on ignore les SSL warnings service_identity
logging.getLogger("service_identity").setLevel(logging.CRITICAL)

def main():
    # 1) Charger la config crawler_config.json
    config = json.load(open(sys.argv[1]))
    settings = get_project_settings()
    for k, v in config.items():
        settings.set(k, v)

    # 2) Connexion Redis & Kafka
    redis = Redis.from_url(settings.get("REDIS_URL"))
    consumer = KafkaConsumer(
        settings.get("CRAWL_TOPIC"),
        bootstrap_servers=[settings.get("KAFKA_BROKER")],
        auto_offset_reset=settings.get("AUTO_OFFSET_RESET"),
        group_id=settings.get("GROUP_ID"),
    )

    # 3) Initialiser Scrapy
    process = CrawlerProcess(settings)

    # 4) Handle SIGTERM proprement
    def shutdown(signum, frame):
        logging.info("Arrêt du crawler…")
        process.stop()
        sys.exit(0)
    signal.signal(signal.SIGTERM, shutdown)

    logging.info("Crawler prêt, en attente de messages Kafka…")
    for msg in consumer:
        url = msg.value.decode()
        logging.info(f"Reçu URL → {url}, push to Redis {settings.get('SPIDER_STARTREDSIS_KEY')}")
        redis.lpush(settings.get("SPIDER_STARTREDIS_KEY"), url)

        # 5) Lancer le spider
        process.crawl(settings.get("SPIDER"))
        process.start(stop_after_crawl=True)  # lance et attend

if __name__ == "__main__":
    main()
