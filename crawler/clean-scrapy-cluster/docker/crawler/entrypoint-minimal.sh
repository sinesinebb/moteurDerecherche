#!/bin/bash
set -e

echo "=== Démarrage du crawler ==="

# Attendre les dépendances
echo "En attente des dépendances..."
echo "Zookeeper: ${ZOOKEEPER_HOSTS:-none}"
echo "Redis: ${REDIS_HOST:-none}:${REDIS_PORT:-none}"
echo "Kafka: ${KAFKA_BOOTSTRAP_SERVERS:-none}"

# Attendre Zookeeper
if [ -n "$ZOOKEEPER_HOSTS" ]; then
    IFS=',' read -ra ZK <<< "$ZOOKEEPER_HOSTS"
    for zk in "${ZK[@]}"; do
        host=$(echo $zk | cut -d: -f1)
        port=$(echo $zk | cut -d: -f2)
        echo "Attente de $host:$port..."
        while ! nc -z $host $port 2>/dev/null; do sleep 1; done
        echo "✓ $host:$port"
    done
fi

# Attendre Redis
if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
    echo "Attente de $REDIS_HOST:$REDIS_PORT..."
    while ! nc -z $REDIS_HOST $REDIS_PORT 2>/dev/null; do sleep 1; done
    echo "✓ Redis"
fi

# Attendre Kafka
if [ -n "$KAFKA_BOOTSTRAP_SERVERS" ]; then
    IFS=',' read -ra KAFKA <<< "$KAFKA_BOOTSTRAP_SERVERS"
    for k in "${KAFKA[@]}"; do
        host=$(echo $k | cut -d: -f1)
        port=$(echo $k | cut -d: -f2)
        echo "Attente de $host:$port..."
        while ! nc -z $host $port 2>/dev/null; do sleep 1; done
        echo "✓ $host:$port"
    done
fi

echo "Toutes les dépendances sont prêtes!"

# Démarrer
cd /usr/src/app/crawler
export PYTHONPATH=/usr/src/app:$PYTHONPATH

echo "Spider: $SPIDER"
echo "Répertoire: $(pwd)"
echo "Fichiers disponibles:"
ls -la || true

# Essayer différentes méthodes de démarrage
if [ -f "run.py" ]; then
    echo "Démarrage avec run.py..."
    exec python run.py
elif [ -f "crawler.py" ]; then
    echo "Démarrage avec crawler.py..."
    exec python crawler.py
else
    echo "Démarrage avec scrapy crawl..."
    exec scrapy crawl "$SPIDER"
fi
