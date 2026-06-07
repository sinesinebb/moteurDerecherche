import json
import time
import logging
import sys
import requests
import re
from datetime import datetime
from confluent_kafka import Consumer, Producer, KafkaError
from config import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("video-fetcher")

# ----------------------------------------------------------------------
# Fonctions utilitaires (hors de main pour être accessibles)
# ----------------------------------------------------------------------
def wait_for_kafka(bootstrap_servers, max_retries=30, delay=2.0):
    """Attend que Kafka soit joignable."""
    for i in range(max_retries):
        try:
            p = Producer({'bootstrap.servers': bootstrap_servers})
            p.list_topics(timeout=5)
            p.flush()
            logger.info("✅ Kafka est accessible")
            return True
        except Exception as e:
            logger.warning(f"⏳ Kafka pas encore prêt ({i+1}/{max_retries}) : {e}")
            time.sleep(delay)
    return False

def fetch_video_details(video_ids: list) -> list:
    """Appelle l'API YouTube pour un lot d'IDs (max 50)."""
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        elif resp.status_code == 403:
            logger.error("Quota YouTube dépassé ou clé invalide (403).")
            return []
        else:
            logger.error(f"YouTube API erreur {resp.status_code}: {resp.text[:200]}")
            return []
    except Exception as e:
        logger.error(f"Erreur appel YouTube: {e}")
        return []

def convert_duration(iso_duration: str) -> int:
    """Convertit une durée ISO 8601 (ex: PT1H23M5S) en secondes."""
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    m = pattern.match(iso_duration)
    if not m:
        return 0
    h, mn, s = m.groups()
    return int(h or 0)*3600 + int(mn or 0)*60 + int(s or 0)

def build_enriched_doc(item, original_msg):
    snippet = item["snippet"]
    stats = item.get("statistics", {})
    content = item.get("contentDetails", {})
    video_id = item["id"]
    return {
        "video_id": video_id,
        "doc_id": original_msg.get("doc_id"),
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "watch_url": f"https://www.youtube.com/watch?v={video_id}",
        "embed_url": f"https://www.youtube.com/embed/{video_id}",
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "tags": snippet.get("tags", []),
        "thumbnail": snippet["thumbnails"].get("high", {}).get("url"),
        "default_thumbnail": snippet["thumbnails"].get("default", {}).get("url"),
        "view_count": int(stats.get("viewCount", 0)),
        "like_count": int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0)),
        "duration_seconds": convert_duration(content.get("duration", "PT0S")),
        "published_at": snippet.get("publishedAt"),
        "channel_title": snippet.get("channelTitle"),
        "source": "youtube",
        "fetched_at": datetime.utcnow().isoformat()
    }

# ----------------------------------------------------------------------
def main():
    logger.info("=== Démarrage du video-fetcher ===")
    if not wait_for_kafka(KAFKA_BOOTSTRAP_SERVERS):
        logger.error("Impossible de se connecter à Kafka, arrêt.")
        sys.exit(1)

    consumer_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
    }
    producer_conf = {'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS}

    consumer = Consumer(consumer_conf)
    producer = Producer(producer_conf)
    consumer.subscribe([CONSUMER_TOPIC])
    logger.info(f"Abonné au topic {CONSUMER_TOPIC}")

    def delivery_callback(err, msg):
        if err:
            logger.error(f"Erreur d'envoi: {err}")
        else:
            logger.debug(f"Envoyé à {msg.topic()} [{msg.partition()}] offset {msg.offset()}")

    def process_batch(video_ids, msgs):
        if not video_ids:
            return
        logger.info(f"🔍 Récupération des détails pour {len(video_ids)} vidéos")
        items = fetch_video_details(video_ids)   # mainteant définie
        by_id = {item["id"]: item for item in items}
        for orig in msgs:
            vid = orig["video_id"]
            if vid in by_id:
                enriched = build_enriched_doc(by_id[vid], orig)
                producer.produce(PRODUCER_TOPIC, key=vid,
                                 value=json.dumps(enriched).encode('utf-8'),
                                 callback=delivery_callback)
            else:
                logger.info(f"Vidéo {vid} indisponible, on marque comme unavailable")
                producer.produce(PRODUCER_TOPIC, key=vid,
                                 value=json.dumps({"video_id": vid, "doc_id": orig.get("doc_id"), "status": "unavailable"}).encode('utf-8'),
                                 callback=delivery_callback)
        producer.flush()
        consumer.commit(asynchronous=True)

    pending_ids = []
    pending_msgs = []
    last_batch_time = time.time()

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            now = time.time()

            if msg is None:
                # Flush automatique après 5 secondes d'inactivité si le buffer n'est pas vide
                if pending_ids and (now - last_batch_time >= 5.0):
                    process_batch(pending_ids, pending_msgs)
                    pending_ids = []
                    pending_msgs = []
                    last_batch_time = now
                continue

            last_batch_time = now   # réinitialiser le timer dès qu'on reçoit un message

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"Erreur consumer: {msg.error()}")
                    continue

            try:
                data = json.loads(msg.value().decode('utf-8'))
                video_id = data.get("video_id")
                if not video_id:
                    logger.warning(f"Message sans video_id ignoré: {data}")
                    continue
                pending_ids.append(video_id)
                pending_msgs.append(data)
            except Exception as e:
                logger.error(f"Message invalide: {e}")

            # Si le lot atteint BATCH_SIZE, on le traite immédiatement
            if len(pending_ids) >= BATCH_SIZE:
                process_batch(pending_ids[:BATCH_SIZE], pending_msgs[:BATCH_SIZE])
                pending_ids = pending_ids[BATCH_SIZE:]
                pending_msgs = pending_msgs[BATCH_SIZE:]

    except KeyboardInterrupt:
        logger.info("Arrêt demandé")
    finally:
        if pending_ids:
            process_batch(pending_ids, pending_msgs)
        consumer.close()
        logger.info("Consumer fermé")

if __name__ == "__main__":
    main()