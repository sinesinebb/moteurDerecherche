# apps/stats/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from elasticsearch import Elasticsearch
from django.conf import settings
from datetime import datetime, timedelta
import pytz
import requests


class DashboardStats(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser and getattr(request.user, 'role', '') != 'admin':
            return Response({'error': 'Accès refusé'}, status=403)

        es = Elasticsearch([f"http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"])
        doc_count = 0
        if es.indices.exists(index='tech_docs'):
            doc_count = es.count(index='tech_docs')['count']

        searches_today = 0   # pourrait venir d'un index ou d'un cache
        active_users = 0
        new_users_today = 0
        try:
            resp = requests.get(f"{settings.USER_SERVICE_URL}/api/users/stats/", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                active_users = data.get('active_users', 0)
                new_users_today = data.get('new_today', 0)
        except:
            pass

        services_list = [
            {'name': 'user-service', 'url': f"{settings.USER_SERVICE_URL}/health"},
            {'name': 'search-service', 'url': f"{settings.SEARCH_SERVICE_URL}/health"},
            {'name': 'indexing-service', 'url': 'http://indexing-service:8001/health'},
            {'name': 'nlp-service', 'url': f"{settings.NLP_SERVICE_URL}/health"},
            {'name': 'pagerank-service', 'url': f"{settings.PAGERANK_SERVICE_URL}/health"},
            {'name': 'admin-service', 'url': 'http://admin-service:8005/health'},
            {'name': 'nginx-gateway', 'url': 'http://nginx-gateway:80/health'},
        ]
        online = 0
        for svc in services_list:
            try:
                r = requests.get(svc['url'], timeout=1)
                if r.status_code < 500:
                    online += 1
            except:
                pass

        return Response({
            'documents': doc_count,
            'documentsChange': 12,
            'searchesToday': searches_today,
            'searchesChange': 8,
            'activeUsers': active_users,
            'newUsersToday': new_users_today,
            'servicesOnline': online,
            'totalServices': len(services_list),
            'systemHealth': 'Stable'
        })


class ActivityView(APIView):
    """Retourne le nombre de documents indexés par heure sur les dernières 24h."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser and getattr(request.user, 'role', '') != 'admin':
            return Response({'error': 'Accès refusé'}, status=403)

        es = Elasticsearch([f"http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"])
        now = datetime.utcnow()
        start = now - timedelta(hours=24)

        # Agrégation par heure (champ crawled_at)
        query = {
            "size": 0,
            "query": {
                "range": {
                    "crawled_at": {
                        "gte": start.isoformat(),
                        "lt": now.isoformat()
                    }
                }
            },
            "aggs": {
                "docs_per_hour": {
                    "date_histogram": {
                        "field": "crawled_at",
                        "fixed_interval": "1h",
                        "min_doc_count": 0,
                        "extended_bounds": {
                            "min": start.isoformat(),
                            "max": now.isoformat()
                        }
                    }
                }
            }
        }

        try:
            if es.indices.exists(index="tech_docs"):
                result = es.search(index="tech_docs", body=query)
                buckets = result['aggregations']['docs_per_hour']['buckets']
                activity = []
                for bucket in buckets:
                    # Convertir la clé (timestamp) en heure locale
                    dt = datetime.utcfromtimestamp(bucket['key'] / 1000.0)
                    hour_str = dt.strftime('%H:%M')
                    activity.append({
                        'time': hour_str,
                        'count': bucket['doc_count']
                    })
                return Response(activity)
            else:
                return Response([])
        except Exception as e:
            return Response([], status=500)  # en cas d'erreur, tableau vide