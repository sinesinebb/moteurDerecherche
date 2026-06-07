from celery import shared_task
from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
import redis
from django.conf import settings
from core.models import MetricSnapshot

@shared_task
def collect_kafka_metrics():
    try:
        consumer = KafkaConsumer(
            'crawled_documents',
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id='admin-collector',
            enable_auto_commit=False
        )
        partitions = consumer.assignment()
        total = 0
        for tp in partitions:
            consumer.seek_to_end(tp)
            total += consumer.position(tp)
        consumer.close()
        MetricSnapshot.objects.create(
            name='kafka.crawled_documents.lag',
            value=total,
            tags={'topic': 'crawled_documents'}
        )
    except Exception as e:
        # log error
        pass

@shared_task
def collect_redis_metrics():
    try:
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        info = r.info()
        MetricSnapshot.objects.create(
            name='redis.used_memory',
            value=info['used_memory'],
            tags={}
        )
    except Exception as e:
        pass

@shared_task
def collect_all_metrics():
    collect_elasticsearch_metrics.delay()
    collect_kafka_metrics.delay()
    collect_redis_metrics.delay()