from rest_framework.routers import DefaultRouter
from apps.configuration.views import ConfigViewSet  # à transformer en ViewSet

router = DefaultRouter()
router.register(r'config', ConfigViewSet, basename='config')