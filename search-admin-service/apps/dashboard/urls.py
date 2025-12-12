from django.urls import path
from . import views

urlpatterns = [
    path('api/dashboard/overview/', views.DashboardOverview.as_view(), name='dashboard_overview'),
    path('api/analytics/search/', views.SearchAnalyticsView.as_view(), name='search_analytics'),
    path('api/analytics/crawl/', views.CrawlAnalyticsView.as_view(), name='crawl_analytics'),
    path('api/config/ranking/', views.RankingConfigView.as_view(), name='ranking_config'),
    path('api/moderation/content/', views.ContentModerationView.as_view(), name='content_moderation'),
]