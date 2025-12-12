from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import TruncHour, TruncDay

from app.models.analytics import SearchAnalytics, CrawlStats, PerformanceMetrics, SystemHealth

class DashboardOverview(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Période : dernières 24 heures
        last_24h = timezone.now() - timedelta(hours=24)
        
        # Métriques de recherche
        search_stats = SearchAnalytics.objects.filter(
            timestamp__gte=last_24h
        ).aggregate(
            total_searches=Count('id'),
            unique_queries=Count('query', distinct=True),
            avg_response_time=Avg('response_time'),
            click_rate=Count('id', filter=Q(user_clicked=True)) * 100.0 / Count('id'),
            zero_results=Count('id', filter=Q(results_count=0))
        )
        
        # Métriques de crawl
        crawl_stats = CrawlStats.objects.filter(
            timestamp__gte=last_24h
        ).aggregate(
            total_crawls=Count('id'),
            success_rate=Count('id', filter=Q(status='success')) * 100.0 / Count('id'),
            avg_crawl_time=Avg('crawl_duration'),
            total_data=Count('id', filter=Q(status='success'))  # Simplifié
        )
        
        # Santé du système
        system_health = SystemHealth.objects.all().values('service_name', 'status', 'last_check')
        
        # Tendances des recherches (par heure)
        search_trends = SearchAnalytics.objects.filter(
            timestamp__gte=last_24h
        ).annotate(
            hour=TruncHour('timestamp')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        
        return Response({
            'search_metrics': search_stats,
            'crawl_metrics': crawl_stats,
            'system_health': list(system_health),
            'search_trends': list(search_trends),
            'time_period': '24h'
        })

class SearchAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        days = int(request.GET.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # Requêtes populaires
        popular_queries = SearchAnalytics.objects.filter(
            timestamp__gte=start_date
        ).values('query').annotate(
            count=Count('id'),
            avg_results=Avg('results_count'),
            click_rate=Count('id', filter=Q(user_clicked=True)) * 100.0 / Count('id')
        ).order_by('-count')[:20]
        
        # Performances par période
        performance_by_hour = SearchAnalytics.objects.filter(
            timestamp__gte=start_date
        ).annotate(
            hour=TruncHour('timestamp')
        ).values('hour').annotate(
            avg_response_time=Avg('response_time'),
            search_count=Count('id')
        ).order_by('hour')
        
        return Response({
            'popular_queries': list(popular_queries),
            'performance_trends': list(performance_by_hour),
            'period_days': days
        })

class CrawlAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        days = int(request.GET.get('days', 1))
        start_date = timezone.now() - timedelta(days=days)
        
        # Statistiques par domaine
        domain_stats = CrawlStats.objects.filter(
            timestamp__gte=start_date
        ).values('domain').annotate(
            total=Count('id'),
            success=Count('id', filter=Q(status='success')),
            avg_size=Avg('page_size'),
            avg_time=Avg('crawl_duration')
        ).order_by('-total')[:50]
        
        # Erreurs récentes
        recent_errors = CrawlStats.objects.filter(
            status__in=['error', 'blocked'],
            timestamp__gte=start_date
        ).values('url', 'status_code', 'error_message', 'timestamp')[:100]
        
        return Response({
            'domain_stats': list(domain_stats),
            'recent_errors': list(recent_errors)
        })