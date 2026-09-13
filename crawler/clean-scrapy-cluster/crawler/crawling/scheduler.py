#!/usr/bin/env python3
# coding: utf-8

import time
import json
import argparse
import logging

from kazoo.client import KazooClient
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import redis

# Configure logging
logger = logging.getLogger("scheduler")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Scheduler pour Scrapy-Cluster")
    parser.add_argument(
        '-c', '--config', required=True,
        help='Chemin vers le fichier JSON de configuration'
    )
    args = parser.parse_args()

    full_cfg = load_config(args.config)
    cfg = full_cfg.get('scheduler', {})

    # Logging level
    level = cfg.get('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, level, logging.INFO))
    logger.info(f"Démarrage scheduler avec : {cfg}")

    # Zookeeper
    zk_hosts = cfg.get('zookeeper_hosts', 'zookeeper:2181')
    zk = KazooClient(hosts=zk_hosts)
    zk.start()
    logger.info(f"Connecté à Zookeeper → {zk_hosts}")

    # Redis client
    redis_url = cfg.get('REDIS_URL', 'redis://redis:6379')
    redis_key = cfg.get('SPIDER_STARTREDIS_KEY', 'sc:start_urls')
    try:
        redis_client = redis.from_url(redis_url)
        logger.info(f"Connecté à Redis → {redis_url}, clé = {redis_key}")
    except Exception as e:
        logger.error(f"Impossible de connecter Redis: {e}")
        return

    # Kafka bootstrap servers
    kafka_servers = cfg.get('KAFKA_BROKER') or cfg.get('KAFKA_BOOTSTRAP_SERVERS')
    if isinstance(kafka_servers, str):
        kafka_servers = [kafka_servers]
    kafka_servers = kafka_servers or ['kafka:9092']

    # Topics
    seed_topic  = cfg.get('SEED_TOPIC')
    crawl_topic = cfg.get('CRAWL_TOPIC')
    if not seed_topic or not crawl_topic:
        logger.error("SEED_TOPIC et CRAWL_TOPIC doivent être définis")
        return

    # Consumer pour lire les seeds
    consumer = KafkaConsumer(
        seed_topic,
        bootstrap_servers=kafka_servers,
        group_id=cfg.get('GROUP_ID', 'scheduler-group'),
        auto_offset_reset=cfg.get('AUTO_OFFSET_RESET', 'earliest'),
        value_deserializer=lambda m: m.decode('utf-8'),
    )
    logger.info(f"Abonné au topic Seeds → {seed_topic}")

    # Producer pour publier les crawl requests
    producer = KafkaProducer(
        bootstrap_servers=kafka_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    logger.info(f"Connecté à Kafka Producer → {kafka_servers}")

    interval = cfg.get('INTERVAL', 5)

    try:
        while True:
            # 1) Récupérer les nouvelles seeds
            records = consumer.poll(timeout_ms=1000)
            if records:
                for tp, msgs in records.items():
                    for msg in msgs:
                        url = msg.value
                        logger.info(f"Nouvelle seed reçue: {url}")

                        # 2) On pousse dans Redis pour que RedisCrawlSpider la prenne
                        try:
                            redis_client.lpush(redis_key, url)
                            logger.info(f"Pushed seed into Redis {redis_key}: {url}")
                        except Exception as e:
                            logger.error(f"Erreur Redis LPUSH: {e}")

                        # 3) On publie aussi un message de crawl sur Kafka
                        payload = {'url': url, 'timestamp': time.time()}
                        try:
                            producer.send(crawl_topic, payload)
                            logger.info(f"Publié dans {crawl_topic}: {url}")
                        except KafkaError as e:
                            logger.error(f"Erreur envoi crawl request: {e}")

                # 4) Enfin on flush tous les messages Kafka
                producer.flush()
            else:
                logger.debug("Aucune seed nouvelle, attente...")

            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("Arrêt demandé, fermeture...")

    finally:
        consumer.close()
        producer.close()
        zk.stop()
        logger.info("Scheduler terminé")


if __name__ == '__main__':
    main()
