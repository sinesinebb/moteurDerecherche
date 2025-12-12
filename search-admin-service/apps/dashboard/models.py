from django.db import models

# Create your models here.



from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SearchAnalytics(models.Model):
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

class RankingConfig(models.Model):
    CONFIG_TYPE_CHOICES = [
        ('pagerank', 'PageRank'),
        ('relevance', 'Pertinence'),
        ('boosting', 'Boosting'),
        ('filtering', 'Filtrage'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPE_CHOICES)
    value = models.FloatField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'ranking_config'

class ContentModeration(models.Model):
    MODERATION_TYPE_CHOICES = [
        ('url_blacklist', 'URL Blacklist'),
        ('domain_blacklist', 'Domain Blacklist'),
        ('content_filter', 'Filtre de Contenu'),
        ('spam_detection', 'Détection de Spam'),
    ]
    
    moderation_type = models.CharField(max_length=20, choices=MODERATION_TYPE_CHOICES)
    target = models.CharField(max_length=2000)  # URL, domaine, mot-clé
    reason = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'content_moderation'
        indexes = [
            models.Index(fields=['moderation_type', 'is_active']),
        ]

class CrawlConfig(models.Model):
    name = models.CharField(max_length=100, unique=True)
    max_pages_per_domain = models.IntegerField(default=1000)
    crawl_delay = models.FloatField(default=1.0)
    user_agent = models.CharField(max_length=255, default='SearchBot/1.0')
    respect_robots_txt = models.BooleanField(default=True)
    max_depth = models.IntegerField(default=10)
    
    class Meta:
        db_table = 'crawl_config'