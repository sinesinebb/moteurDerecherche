# apps/stats/urls.py
from django.urls import path
from .views import DashboardStats, ActivityView

urlpatterns = [
    path('dashboard/', DashboardStats.as_view(), name='dashboard-stats'),
    path('activity/', ActivityView.as_view(), name='activity'),
    path('activity/', ActivityView.as_view(), name='activity'),
]