from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.monitoring.views import prometheus_query_proxy 
from django.urls import re_path 
from apps.monitoring.views import health_check

schema_view = get_schema_view(
    openapi.Info(
        title="Admin Service API",
        default_version='v1',
        description="API pour l'administration du moteur de recherche",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('metrics/query', prometheus_query_proxy, name='prometheus-query'),
    # path('metrics/query/', prometheus_query_proxy, name='prometheus-query'),
    path('metrics/query/', prometheus_query_proxy, name='prometheus-query-slash'), 
    # re_path(r'^metrics/query/?$', prometheus_query_proxy, name='prometheus-query'),
    path('api/v1/', include('api.v1.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include('django_prometheus.urls')),
    path('health/', health_check, name='health'),
]

