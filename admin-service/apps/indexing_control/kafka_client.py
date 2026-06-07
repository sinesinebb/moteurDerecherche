from kafka import KafkaProducer
import json
from django.conf import settings

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_crawler_command(command, payload=None):
    data = {'command': command, 'payload': payload or {}}
    producer.send('admin.commands', value=data)
    producer.flush()