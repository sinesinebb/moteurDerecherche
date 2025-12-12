
# ——— Clés d'environnement ———
ENV_KAFKA_BROKERS      = "KAFKA_BROKERS"
ENV_KAFKA_TOPIC        = "KAFKA_TOPIC"
ENV_KAFKA_GROUP_ID     = "KAFKA_GROUP_ID"

ENV_ES_HOSTS           = "ES_HOSTS"
ENV_ES_INDEX           = "ES_INDEX"
ENV_ES_REQUEST_TIMEOUT = "ES_REQUEST_TIMEOUT"

ENV_MINIO_ENDPOINT     = "MINIO_ENDPOINT"
ENV_MINIO_ACCESS_KEY   = "MINIO_ACCESS_KEY"
ENV_MINIO_SECRET_KEY   = "MINIO_SECRET_KEY"
ENV_MINIO_BUCKET       = "MINIO_BUCKET"

ENV_REDIS_HOST         = "REDIS_HOST"
ENV_REDIS_PORT         = "REDIS_PORT"
ENV_REDIS_DB           = "REDIS_DB"

ENV_LOG_LEVEL          = "LOG_LEVEL"
ENV_ENVIRONMENT        = "ENVIRONMENT"
ENV_SERVICE_PORT       = "SERVICE_PORT"
ENV_TEMP_DIR           = "TEMP_DIR"

# ——— Valeurs par défaut ———
DEFAULT_KAFKA_GROUP_ID = "indexer-group"
DEFAULT_ES_REQUEST_TIMEOUT = 30  # secondes
DEFAULT_REDIS_DB        = 0

# ——— Ports et chemins ———
DEFAULT_SERVICE_PORT   = 8000
DEFAULT_TEMP_DIR       = "/app/tmp"

# ——— Mapping interne (si utile) ———
# Vous pouvez aussi définir ici des constantes métiers,
# comme le nom du topic pour l'indexation supplémentaire :
TOPIC_ENRICHED_DOCS    = "enriched_documents"

