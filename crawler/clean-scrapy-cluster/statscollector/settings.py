import os

# Kafka
KAFKA_HOSTS    = os.environ.get('KAFKA_HOSTS', 'kafka:9092').split(',')
KAFKA_TOPIC    = os.environ.get('KAFKA_TOPIC', 'stats')
KAFKA_GROUP_ID = os.environ.get('KAFKA_GROUP_ID', 'stats_collector')

# Intervalle d’émission des stats (en secondes)
EMIT_INTERVAL = int(os.environ.get('STATS_EMIT_INTERVAL', 60))

# Redis (si nécessaire)
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
