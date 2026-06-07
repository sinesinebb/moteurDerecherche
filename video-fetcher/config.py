import os

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY must be set")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
CONSUMER_TOPIC = os.getenv("YOUTUBE_REQUEST_TOPIC", "youtube.metadata.requests")
PRODUCER_TOPIC = os.getenv("YOUTUBE_UPDATED_TOPIC", "youtube.metadata.updated")
GROUP_ID = os.getenv("GROUP_ID", "video-fetcher")

# Batching
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 20))        # Nombre d'IDs par requête
FETCH_INTERVAL = float(os.getenv("FETCH_INTERVAL", 1.0))  # secondes entre lots

# Quota gestion
QUOTA_RETRY_SLEEP = int(os.getenv("QUOTA_RETRY_SLEEP", 300)) # 5 minutes