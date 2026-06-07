from django.urls import path, include

urlpatterns = [
    path('users/', include('apps.users.urls')),
    path('config/', include('apps.configuration.urls')),
    path('monitoring/', include('apps.monitoring.urls')),
    path('indexing/', include('apps.indexing_control.urls')),
    path('stats/', include('apps.stats.urls')),
    
]
