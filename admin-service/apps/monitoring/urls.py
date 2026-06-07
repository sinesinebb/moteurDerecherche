# apps/monitoring/urls.py
from django.urls import path
from .views import (
    health_check, ServiceStatus, ServiceRestartView, ServiceLogsView,
    prometheus_query_proxy
)

urlpatterns = [
    path('health/', health_check, name='monitoring-health'),
    path('services/', ServiceStatus.as_view(), name='service-status'),
    path('services/restart/', ServiceRestartView.as_view(), name='service-restart'),
    path('services/logs/', ServiceLogsView.as_view(), name='service-logs'),
    path('metrics/query/', prometheus_query_proxy, name='prometheus-query'),
]
