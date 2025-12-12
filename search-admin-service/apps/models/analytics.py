from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class SearchAnalytics(models.Model):
    """Analytics des recherches utilisateur"""
    query = models.CharField(max_length=500, db_index=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    results_count = models.IntegerField(default=0)
    response_time = models.FloatField()  # en millisecondes
    user_clicked = models.BooleanField(default=False)
    user_id = models.CharField(max_length=100, blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'search_analytics'
        indexes = [
            models.Index(fields=['query', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user_id', 'timestamp']),
        ]
        ordering = ['-timestamp']

class CrawlStats(models.Model):
    """Statistiques de crawling"""
    CRAWL_STATUS_CHOICES = [
        ('success', 'Succès'),
        ('error', 'Erreur'),
        ('blocked', 'Bloqué'),
        ('redirect', 'Redirection'),
    ]
    
    url = models.URLField(max_length=2000)
    domain = models.CharField(max_length=255, db_index=True)
    status_code = models.IntegerField()
    status = models.CharField(max_length=10, choices=CRAWL_STATUS_CHOICES)
    crawl_duration = models.FloatField()  # en secondes
    page_size = models.IntegerField()  # en bytes
    content_type = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'crawl_stats'
        indexes = [
            models.Index(fields=['domain', 'timestamp']),
            models.Index(fields=['status', 'timestamp']),
        ]

class PerformanceMetrics(models.Model):
    """Métriques de performance des services"""
    metric_name = models.CharField(max_length=100, db_index=True)
    metric_value = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    service = models.CharField(max_length=50)  # search, crawl, index, etc.
    
    class Meta:
        db_table = 'performance_metrics'
        indexes = [
            models.Index(fields=['metric_name', 'timestamp']),
            models.Index(fields=['service', 'timestamp']),
        ]

class SystemHealth(models.Model):
    """Santé des services du moteur"""
    service_name = models.CharField(max_length=50)
    status = models.CharField(max_length=20)  # healthy, degraded, down
    last_check = models.DateTimeField(default=timezone.now)
    response_time = models.FloatField()
    error_rate = models.FloatField(default=0.0)
    details = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'system_health'
        indexes = [
            models.Index(fields=['service_name', 'last_check']),
        ]