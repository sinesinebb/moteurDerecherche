from django.db import models

class RankingConfig(models.Model):
    """Configuration du ranking et PageRank"""
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
    """Modération de contenu et blacklists"""
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
    """Configuration du crawling"""
    name = models.CharField(max_length=100, unique=True)
    max_pages_per_domain = models.IntegerField(default=1000)
    crawl_delay = models.FloatField(default=1.0)
    user_agent = models.CharField(max_length=255, default='SearchBot/1.0')
    respect_robots_txt = models.BooleanField(default=True)
    max_depth = models.IntegerField(default=10)
    
    class Meta:
        db_table = 'crawl_config'