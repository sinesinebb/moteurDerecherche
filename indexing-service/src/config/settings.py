import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKERS  = os.getenv("KAFKA_BROKERS")
KAFKA_TOPIC    = os.getenv("KAFKA_TOPIC")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "indexer-group")
ES_INDEX       = os.getenv("ES_INDEX")
ES_HOSTS       = os.getenv("ES_HOSTS", "http://elasticsearch:9200")
ES_USER        = os.getenv("ES_USER")
ES_PASSWORD    = os.getenv("ES_PASSWORD")



REDIS_HOST         = os.getenv("REDIS_HOST")
REDIS_PORT         = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB           = int(os.getenv("REDIS_DB", 0))

SERVICE_PORT       = int(os.getenv("SERVICE_PORT", 8000))
TEMP_DIR           = os.getenv("TEMP_DIR", "/tmp")

