# apps/monitoring/views.py
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse
import requests
import docker
import time
from datetime import datetime, timedelta


@api_view(['GET'])
def prometheus_query_proxy(request):
    """Proxy vers l'API Prometheus (query_range)."""
    if not request.user or not request.user.is_authenticated:
        return Response({'error': 'Authentification requise'}, status=401)
    if not request.user.is_superuser and getattr(request.user, 'role', '') != 'admin':
        return Response({'error': 'Accès refusé'}, status=403)

    query = request.query_params.get('query')
    start_str = request.query_params.get('start', 'now-1h')
    end_str = request.query_params.get('end', 'now')
    step = request.query_params.get('step', '15s')

    if not query:
        return Response({'error': 'Missing query parameter'}, status=400)

    def parse_time(t):
        if t == 'now':
            return time.time()
        if t.startswith('now-'):
            parts = t.split('-')
            if len(parts) == 2:
                value = parts[1]
                unit = value[-1]
                num = int(value[:-1])
                delta_map = {'h': timedelta(hours=num),
                             'm': timedelta(minutes=num),
                             's': timedelta(seconds=num)}
                delta = delta_map.get(unit, timedelta(seconds=0))
                return (datetime.now() - delta).timestamp()
        try:
            return float(t)
        except:
            return time.time() - 3600

    prometheus_url = 'http://prometheus:9090/api/v1/query_range'
    params = {
        'query': query,
        'start': parse_time(start_str),
        'end': parse_time(end_str),
        'step': step
    }
    try:
        resp = requests.get(prometheus_url, params=params, timeout=10)
        resp.raise_for_status()
        return Response(resp.json())
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=500)


def health_check(request):
    return JsonResponse({"status": "ok", "service": "admin-service"})


class ServiceStatus(APIView):
    """Vérifie l'état de tous les conteneurs Docker (microservices + infrastructure)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser and getattr(request.user, 'role', '') != 'admin':
            return Response({'error': 'Accès refusé'}, status=403)

        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        # Récupérer tous les conteneurs (même arrêtés)
        all_containers = {c.name: c for c in client.containers.list(all=True)}

        # Noms exacts des conteneurs (tels que retournés par `docker ps`)
        services = [
            {'name': 'scrapy-crawler',                                 'label': 'Crawler Service'},
            {'name': 'scrapy-scheduler',                               'label': 'Scrapy Scheduler'},
            {'name': 'moteur_recherche-indexing-service-1',            'label': 'Indexing Service'},
            {'name': 'moteur_recherche-search-service-1',             'label': 'Search Service'},
            {'name': 'moteur_recherche-nlp-service-1',                 'label': 'NLP Service'},
            {'name': 'moteur_recherche-pagerank-service-1',            'label': 'PageRank Service'},
            {'name': 'user-service',                                   'label': 'User Service'},
            {'name': 'moteur_recherche-admin-service-1',               'label': 'Admin Service'},
            {'name': 'nginx-gateway',                                  'label': 'Nginx Gateway'},
            {'name': 'frontend-nuxt',                                  'label': 'Frontend'},
            {'name': 'kafka',                                          'label': 'Kafka'},
            {'name': 'redis',                                          'label': 'Redis'},
            {'name': 'zookeeper',                                      'label': 'Zookeeper'},
            {'name': 'elasticsearch',                                  'label': 'Elasticsearch'},
            {'name': 'minio',                                          'label': 'MinIO'},
            {'name': 'admin-db',                                       'label': 'Admin DB'},
            {'name': 'mailhog',                                        'label': 'MailHog'},
            {'name': 'user-db',                                        'label': 'User DB'},
            {'name': 'grafana',                                        'label': 'Grafana'},
            {'name': 'prometheus',                                     'label': 'Prometheus'},
        ]

        results = []
        for svc in services:
            container = all_containers.get(svc['name'])
            if container:
                if container.status == 'running':
                    stat = 'online'
                elif 'restart' in container.status.lower():
                    stat = 'warning'
                else:
                    stat = 'offline'
            else:
                # Si le conteneur n'est pas trouvé dans Docker, on tente un healthcheck HTTP si l'URL existe
                stat = 'offline'
                # (optionnel) ex: forcer une URL de healthcheck connue
                # if svc['name'] == 'kafka':
                #     try: requests.get('http://kafka:9092', timeout=1); stat='online'
                #     except: pass

            results.append({
                'name': svc['name'],
                'label': svc['label'],
                'description': f"Conteneur {svc['label']}",
                'status': stat,
                'uptime': 'N/A',
                'responseTime': 'N/A',
                'icon': 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
            })

        return Response(results)


class ServiceRestartView(APIView):
    """Redémarre un conteneur Docker."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser and getattr(request.user, 'role', '') != 'admin':
            return Response({'error': 'Accès refusé'}, status=403)
        service_name = request.data.get('name')
        if not service_name:
            return Response({'error': 'Nom du service requis'}, status=400)
        try:
            client = docker.DockerClient(base_url='unix://var/run/docker.sock')
            # Rechercher un conteneur dont le nom contient service_name
            containers = [c for c in client.containers.list() if service_name in c.name]
            if not containers:
                return Response({'error': f'Conteneur contenant "{service_name}" introuvable'}, status=404)
            containers[0].restart()
            return Response({'message': f'Redémarrage de {service_name} en cours'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class ServiceLogsView(APIView):
    """Récupère les logs d'un ou plusieurs conteneurs."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser and getattr(request.user, 'role', '') != 'admin':
            return Response({'error': 'Accès refusé'}, status=403)
        service_name = request.query_params.get('service')
        lines = request.query_params.get('lines', 50)
        try:
            client = docker.DockerClient(base_url='unix://var/run/docker.sock')
            if service_name:
                containers = [c for c in client.containers.list() if service_name in c.name]
            else:
                containers = client.containers.list()
            logs_data = []
            for c in containers:
                log = c.logs(tail=int(lines), timestamps=True)
                logs_data.append({
                    'container': c.name,
                    'logs': log.decode('utf-8').splitlines()
                })
            return Response({'logs': logs_data})
        except Exception as e:
            return Response({'error': str(e)}, status=500)