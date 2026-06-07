from kafka import KafkaProducer
import json
from django.conf import settings

def get_producer():
    return KafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def publish_event(topic, event):
    producer = get_producer()
    producer.send(topic, value=event)
    producer.flush()