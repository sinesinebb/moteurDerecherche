import os

# Redis (stockage des queues)
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB   = int(os.environ.get('REDIS_DB', 0))

# Zookeeper (pour config dynamique)
ZOOKEEPER_HOSTS = os.environ.get('ZOOKEEPER_HOSTS', 'zookeeper:2181')
ZOOKEEPER_ID    = os.environ.get('ZOOKEEPER_ID', 'all')
ZOOKEEPER_ASSIGN_PATH = os.environ.get('ZOOKEEPER_ASSIGN_PATH', '/sc/config/')

# Paramètres de throttling par défaut
QUEUE_HITS      = int(os.environ.get('QUEUE_HITS', 10))
QUEUE_WINDOW    = int(os.environ.get('QUEUE_WINDOW', 60))
QUEUE_MODERATED = os.environ.get('QUEUE_MODERATED', 'false').lower() in ('1','true')
