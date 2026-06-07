# apps/configuration/urls.py
from django.urls import path
from .views import (
    ConfigList, ConfigDetail, ClearCacheView, BackupView
)

urlpatterns = [
    path('', ConfigList.as_view(), name='config-list'),
    path('<str:key>/', ConfigDetail.as_view(), name='config-detail'),
    path('cache/clear/', ClearCacheView.as_view(), name='clear-cache'),
    path('backup/', BackupView.as_view(), name='backup'),
]