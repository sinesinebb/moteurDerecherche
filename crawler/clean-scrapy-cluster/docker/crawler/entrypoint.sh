#!/bin/bash
set -e

echo "=== Scrapy Crawler Entrypoint ==="
cd /usr/src/app/crawler

# Attendre que Kafka/Zookeeper soient prêts (optionnel)
echo "Attente des services..."
while ! nc -z kafka 9092; do sleep 1; done
while ! nc -z zookeeper 2181; do sleep 1; done
echo "Tous les services sont prêts."

echo "Lancement du spider infoscraper..."
exec scrapy crawl infoscraper