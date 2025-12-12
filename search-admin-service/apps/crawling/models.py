# models.py
class CrawlStats(models.Model):
    crawler_id = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    urls_crawled = models.IntegerField(default=0)
    urls_failed = models.IntegerField(default=0)
    avg_crawl_time = models.FloatField(default=0)
    total_size_mb = models.FloatField(default=0)
    
class CrawlerStatus(models.Model):
    worker_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[('running', 'Running'), ('idle', 'Idle'), ('error', 'Error')])
    last_heartbeat = models.DateTimeField()
    queue_size = models.IntegerField(default=0)
    current_url = models.URLField(blank=True)
    
class CrawlQueue(models.Model):
    url = models.URLField()
    priority = models.IntegerField(default=1)  # 1-10, 10 highest
    added_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')])
    retry_count = models.IntegerField(default=0)