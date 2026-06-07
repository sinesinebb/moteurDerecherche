from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
from django.conf import settings

@api_view(['GET'])
# @permission_classes([IsAuthenticated])  # ou IsAdminUser
def prometheus_query(request):
    query = request.GET.get('query')
    if not query:
        return Response({'error': 'query parameter required'}, status=400)
    
    # Utiliser l'URL de Prometheus depuis les settings
    prometheus_url = 'http://prometheus:9090/api/v1/query_range' 
    params = {
        'query': query,
        'start': request.GET.get('start', 'now-1h'),
        'end': request.GET.get('end', 'now'),
        'step': request.GET.get('step', '15s')
    }
    try:
        resp = requests.get(prometheus_url, params=params)
        return Response(resp.json())
    except Exception as e:
        return Response({'error': str(e)}, status=500)