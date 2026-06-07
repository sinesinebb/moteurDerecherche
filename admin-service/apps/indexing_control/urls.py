# apps/indexing_control/urls.py
from django.urls import path
from .views import (
    CrawlerStart, CrawlerStop, Reindex, IndexStatus, IndexErrors
)

urlpatterns = [
    path('start/', CrawlerStart.as_view(), name='crawler-start'),
    path('stop/', CrawlerStop.as_view(), name='crawler-stop'),
    path('reindex/', Reindex.as_view(), name='reindex'),
    path('status/', IndexStatus.as_view(), name='index-status'),
    path('errors/', IndexErrors.as_view(), name='index-errors'),
]