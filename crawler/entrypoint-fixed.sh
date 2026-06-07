#!/bin/bash
set -e

echo "=== DÉMARRAGE CRAWLER ==="

# Si le fichier de config n'existe pas, le créer
CONFIG_FILE="/usr/src/app/app/cluster_config/crawler_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Création config par défaut..."
    mkdir -p /usr/src/app/app/cluster_config
    cat > "$CONFIG_FILE" << 'CONFIG'
{
  "redis_host": "redis",
  "redis_port": 6379,
  "redis_password": null,
  "redis_db": 0,
  "redis_timeout": 5,
  "redis_ttl": 86400,
  "zookeeper_hosts": "zookeeper:2181",
  "kafka_hosts": "kafka:9092",
  "kafka_topic": "crawled_documents",
  "spider_name": "infoscraper",
  "spider_module": "crawling.spiders.infoscraper",
  "appid": "moteur-recherche",
  "max_pages_per_domain": 100,
  "max_depth": 3,
  "respect_robots": true,
  "user_agent": "MoteurRechercheBot/1.0",
  "download_delay": 1.0
}
CONFIG
fi

# Test simple
echo "Test Python..."
python3 -c "import sys; print('Python OK')"

# Lancer le crawler
echo "Lancement crawler..."
cd /usr/src/app/crawler
exec python3 crawler.py "$CONFIG_FILE"
