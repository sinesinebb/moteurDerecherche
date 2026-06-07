# apps/configuration/views.py
import redis
from django.conf import settings
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import SystemConfiguration, AuditLog
from core.serializers import SystemConfigSerializer
from core.permissions import IsAdminUser


# CRUD existant
class ConfigList(generics.ListCreateAPIView):
    queryset = SystemConfiguration.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAdminUser]


class ConfigDetail(generics.RetrieveUpdateAPIView):
    queryset = SystemConfiguration.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'key'


class ClearCacheView(APIView):
    """Vide le cache Redis."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            r = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB
            )
            r.flushdb()
            AuditLog.objects.create(
                user_id=request.user.id,
                action='cache_clear',
                details={'command': 'clear_cache'}
            )
            return Response({'message': 'Cache vidé'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class BackupView(APIView):
    """Déclenche une sauvegarde (simulée pour l'instant)."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        # Vous pouvez ici lancer un pg_dump ou une tâche asynchrone
        AuditLog.objects.create(
            user_id=request.user.id,
            action='backup_trigger',
            details={'command': 'backup'}
        )
        return Response({'message': 'Sauvegarde demandée'})