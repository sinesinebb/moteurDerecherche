import os
import json
import argparse
import logging
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic


logging.basicConfig(level=logging.INFO)
log = logging.getLogger("seeder")

def load_config(path):
    with open(path) as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True,
                        help='Path to seeder config JSON')
    args = parser.parse_args()

    config = load_config(args.config)
    log.info("Seeder démarré avec la config : %s", config)

    broker = os.getenv("KAFKA_BROKER", config["kafka"]["bootstrap_servers"])
    topic  = os.getenv("SEED_TOPIC",   config["kafka"]["topics"]["seed"])

    producer = KafkaProducer(
        bootstrap_servers=[broker],
        value_serializer=lambda v: v.encode('utf-8')
    )

    # === création du topic si besoin ===
    # admin = KafkaAdminClient(bootstrap_servers=[broker])
    # try:
    #     admin.create_topics([NewTopic(name=topic, num_partitions=1, replication_factor=1)])
    #     log.info("Topic %s créé", topic)
    # except Exception as e:
    #     log.debug("Topic %s existe déjà ou erreur de création : %s", topic, e)
    # finally:
    #     admin.close()
    # ===================================

    seed_urls = config.get("seed_urls", [])
    if not seed_urls:
        log.warning("Aucune URL de seed trouvée")
    for url in seed_urls:
        log.info("Envoi de la seed %s → topic %s", url, topic)
        producer.send(topic, url)

    producer.flush()
    producer.close()
    log.info("Seeder terminé")

if __name__ == '__main__':
    main()
