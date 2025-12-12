# search_admin/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Search Admin API",
        default_version='v1',
        description="Administration interface for search engine",
    ),
    public=True,
    permission_classes=[permissions.IsAdminUser],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/crawl/', include('apps.crawling.urls')),
    path('api/config/', include('apps.engine_config.urls')),
    path('api/moderation/', include('apps.moderation.urls')),
    path('api/reports/', include('apps.reporting.urls')),
    path('api/system/', include('apps.system.urls')),
    
    # Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Health checks
    path('health/', include('health_check.urls')),
]