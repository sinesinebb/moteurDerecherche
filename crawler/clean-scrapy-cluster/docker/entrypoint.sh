#!/bin/bash
set -e

echo "=== Configuration du crawler Scrapy Cluster ==="

# Attendre que les services dépendants soient prêts
echo "Attente de Redis..."
while ! nc -z redis 6379; do
  sleep 1
done

echo "Attente de Zookeeper..."
while ! nc -z zookeeper 2181; do
  sleep 1
done

echo "Attente de Kafka..."
while ! nc -z kafka 9092; do
  sleep 1
done

echo "=== Tous les services sont prêts ==="

# Définir le PYTHONPATH
export PYTHONPATH=/usr/src/app/crawler:/usr/src/app:$PYTHONPATH

# Tester l'importation des modules
echo "Test d'importation du module crawling..."
python3 -c "import sys; print('Chemin Python:', sys.path); from crawling.spiders import infoscraper; print('✓ Spider infoscraper importé avec succès')"

# Créer le fichier de configuration dynamique
cat > /tmp/crawler_config.json << EOF
{
  "redis_host": "${REDIS_HOST:-redis}",
  "redis_port": ${REDIS_PORT:-6379},
  "redis_password": null,
  "redis_db": 0,
  "redis_timeout": 5,
  "redis_ttl": 86400,
  "zookeeper_hosts": "${ZOOKEEPER_HOSTS:-zookeeper:2181}",
  "kafka_hosts": "${KAFKA_BOOTSTRAP_SERVERS:-kafka:9092}",
  "kafka_topic": "${KAFKA_TOPIC:-crawled_documents}",
  "spider_name": "${SPIDER:-infoscraper}",
  "spider_module": "crawling.spiders.${SPIDER:-infoscraper}",
  "appid": "${CLUSTER_NAME:-moteur-recherche}",
  "max_pages_per_domain": 100,
  "max_depth": 3,
  "respect_robots": true,
  "user_agent": "MoteurRechercheBot/1.0",
  "download_delay": 1.0
}
EOF

echo "=== Fichier de configuration généré ==="
cat /tmp/crawler_config.json

# Démarrer le crawler avec la configuration
echo "=== Démarrage du crawler ==="
cd /usr/src/app/crawler
exec python3 crawler.py /tmp/crawler_config.json