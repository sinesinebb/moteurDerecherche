#!/usr/bin/env python3
# scripts/load_test_data.py
"""
Load test data for development / integration tests.

Behavior (best-effort):
 - If kafka-python is installed and KAFKA_BROKER env set, will produce messages to topic
 - Otherwise will try to bulk-index directly into Elasticsearch (HTTP bulk)
 - Optionally upload a sample file to Minio if minio package and creds present

Usage examples:
  python scripts/load_test_data.py --count 50 --index test-idx
  python scripts/load_test_data.py --kafka-topic mytopic --count 100
"""

from __future__ import annotations
import os
import sys
import json
import time
import random
import argparse
from typing import List

try:
    from kafka import KafkaProducer
except Exception:
    KafkaProducer = None

try:
    from minio import Minio
except Exception:
    Minio = None

try:
    # use requests for Elasticsearch HTTP calls if available
    import requests
except Exception:
    requests = None

DEFAULT_ES = os.getenv("ES_HOSTS", "http://elasticsearch:9200")
DEFAULT_KAFKA = os.getenv("KAFKA_BROKERS", "kafka:9092")
DEFAULT_MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
DEFAULT_MINIO_ACCESS = os.getenv("MINIO_ACCESS_KEY")
DEFAULT_MINIO_SECRET = os.getenv("MINIO_SECRET_KEY")


def gen_doc(i: int) -> dict:
    return {
        "id": f"doc-{i}",
        "text": f"Document sample {i} - random {random.randint(0,1000)}",
        "metadata": {"source": "load_test_data", "n": i},
        # small fake embedding
        "embedding": [round(random.random(), 6) for _ in range(8)],
    }


def bulk_index_http(es_host: str, index_name: str, docs: List[dict]) -> dict:
    """
    Send a simple NDJSON bulk request to Elasticsearch HTTP endpoint.
    es_host: e.g. http://elasticsearch:9200
    """
    if requests is None:
        print("requests package missing — cannot bulk to Elasticsearch via HTTP. Install 'requests' or run via kafka.")
        return {}

    bulk_lines = []
    for d in docs:
        action = {"index": {"_index": index_name, "_id": d.get("id")}}
        bulk_lines.append(json.dumps(action))
        bulk_lines.append(json.dumps(d))
    data = "\n".join(bulk_lines) + "\n"
    url = es_host.rstrip("/") + "/_bulk"
    headers = {"Content-Type": "application/x-ndjson"}
    resp = requests.post(url, headers=headers, data=data, timeout=30)
    try:
        return resp.json()
    except Exception:
        return {"status_code": resp.status_code, "text": resp.text}


def produce_kafka(brokers: str, topic: str, docs: List[dict]) -> bool:
    if KafkaProducer is None:
        print("kafka-python not installed; skipping kafka produce.")
        return False
    print(f"Connecting to Kafka brokers {brokers} ...")
    producer = KafkaProducer(bootstrap_servers=brokers.split(","), value_serializer=lambda v: json.dumps(v).encode())
    for d in docs:
        producer.send(topic, d)
    producer.flush()
    print(f"Produced {len(docs)} messages to {topic}")
    return True


def upload_minio(endpoint, access_key, secret_key, bucket="test-bucket", object_name="sample.txt", content=b"hello"):
    if Minio is None:
        print("minio package not installed; skipping minio upload.")
        return False
    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)
    try:
        found = client.bucket_exists(bucket)
    except Exception as e:
        print("Minio connect error:", e)
        return False
    if not found:
        client.make_bucket(bucket)
    import tempfile
    fname = None
    try:
        tf = tempfile.NamedTemporaryFile(delete=False)
        fname = tf.name
        tf.write(content)
        tf.close()
        client.fput_object(bucket, object_name, fname)
        print("Uploaded sample to Minio:", bucket, object_name)
        return True
    finally:
        if fname and os.path.exists(fname):
            os.remove(fname)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=20, help="number of docs to create")
    parser.add_argument("--index", type=str, default="test-index", help="elasticsearch index name")
    parser.add_argument("--kafka-topic", type=str, default=None, help="kafka topic to produce to (overrides ES)")
    parser.add_argument("--es-host", type=str, default=DEFAULT_ES, help="elasticsearch host (http://host:9200)")
    parser.add_argument("--kafka-brokers", type=str, default=DEFAULT_KAFKA, help="kafka brokers csv")
    parser.add_argument("--minio-upload", action="store_true", help="upload small sample to minio if configured")
    args = parser.parse_args()

    docs = [gen_doc(i) for i in range(args.count)]

    if args.kafka_topic:
        ok = produce_kafka(args.kafka_brokers, args.kafka_topic, docs)
        if ok:
            print("Done producing to Kafka.")
            return

    # fallback to ES HTTP bulk
    print(f"Indexing {len(docs)} documents into ES index {args.index} via HTTP at {args.es_host}")
    res = bulk_index_http(args.es_host, args.index, docs)
    print("ES bulk response summary keys:", list(res.keys()) if isinstance(res, dict) else type(res))
    if args.minio_upload:
        if DEFAULT_MINIO_ACCESS and DEFAULT_MINIO_SECRET:
            upload_minio(DEFAULT_MINIO_ENDPOINT, DEFAULT_MINIO_ACCESS, DEFAULT_MINIO_SECRET)
        else:
            print("Minio credentials not configured; skipping minio upload.")


if __name__ == "__main__":
    main()
