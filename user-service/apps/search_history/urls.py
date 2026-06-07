from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SearchHistoryViewSet, UserPreferenceViewSet

router = DefaultRouter()
router.register(r'', SearchHistoryViewSet, basename='search-history')
router.register(r'preferences', UserPreferenceViewSet, basename='user-preferences')

urlpatterns = [
    path('', include(router.urls)),
    
    # Routes supplémentaires pour les statistiques
    path('analytics/', SearchHistoryViewSet.as_view({'get': 'statistics'}), name='search-analytics'),
    path('export/', SearchHistoryViewSet.as_view({'get': 'export'}), name='export-history'),
]

