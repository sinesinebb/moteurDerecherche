# models.py
class RankingConfig(models.Model):
    name = models.CharField(max_length=100)
    damping_factor = models.FloatField(default=0.85)
    convergence_threshold = models.FloatField(default=0.0001)
    max_iterations = models.IntegerField(default=100)
    link_weight = models.FloatField(default=1.0)
    content_weight = models.FloatField(default=1.0)
    freshness_weight = models.FloatField(default=0.5)
    is_active = models.BooleanField(default=False)
    
class DomainBoost(models.Model):
    domain = models.CharField(max_length=255)
    boost_factor = models.FloatField(default=1.0)
    reason = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
class ContentFilter(models.Model):
    filter_type = models.CharField(max_length=50, choices=[('safesearch', 'SafeSearch'), ('regional', 'Regional'), ('linguistic', 'Linguistic')])
    name = models.CharField(max_length=100)
    config = models.JSONField()  # Configuration flexible
    is_active = models.BooleanField(default=True)