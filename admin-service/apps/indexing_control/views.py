# apps/indexing_control/views.py
import redis
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import AuditLog
from .kafka_client import send_crawler_command
import requests


class CrawlerStart(APIView):
    def post(self, request):
        scrapy_rest_url = "http://scrapy-rest:5343/api/start"
        try:
            resp = requests.post(scrapy_rest_url, json=request.data)
            if resp.status_code == 200:
                AuditLog.objects.create(user_id=request.user.id,
                    action='crawler_control', details={'command': 'start'})
                return Response({'message': 'Crawler started'})
            else:
                return Response({'error': 'Failed to start crawler'}, status=resp.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=503)


class CrawlerStop(APIView):
    def post(self, request):
        scrapy_rest_url = "http://scrapy-rest:5343/api/stop"
        try:
            resp = requests.post(scrapy_rest_url, json=request.data)
            if resp.status_code == 200:
                AuditLog.objects.create(user_id=request.user.id,
                    action='crawler_control', details={'command': 'stop'})
                return Response({'message': 'Crawler stopped'})
            else:
                return Response({'error': 'Failed to stop crawler'}, status=resp.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=503)


class Reindex(APIView):
    """Envoie une commande de réindexation au crawler (ou simulée)."""
    def post(self, request):
        send_crawler_command('reindex', request.data)
        AuditLog.objects.create(user_id=request.user.id,
            action='index_trigger', details={'command': 'reindex'})
        return Response({'message': 'Reindex command sent'})


class IndexStatus(APIView):
    """Taille de la file d'attente Kafka."""
    def get(self, request):
        from kafka import KafkaConsumer
        consumer = KafkaConsumer(
            'crawled_documents',
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id='admin-monitor',
            enable_auto_commit=False
        )
        partitions = consumer.assignment()
        total_messages = 0
        for tp in partitions:
            consumer.seek_to_end(tp)
            total_messages += consumer.position(tp)
        consumer.close()
        return Response({'queue_size': total_messages})


class IndexErrors(APIView):
    """Récupère les messages d'erreur Kafka (topic crawled_documents_errors)."""
    def get(self, request):
        from kafka import KafkaConsumer
        consumer = KafkaConsumer(
            'crawled_documents_errors',
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id='admin-errors',
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )
        errors = []
        for msg in consumer:
            errors.append({
                'offset': msg.offset,
                'value': msg.value.decode('utf-8') if msg.value else None,
                'timestamp': msg.timestamp
            })
            if len(errors) >= 100:
                break
        consumer.close()
        return Response(errors)