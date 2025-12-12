# models.py
class BlacklistItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('domain', 'Domain'),
        ('url', 'URL'),
        ('keyword', 'Keyword'),
        ('ip', 'IP Address'),
    ]
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    value = models.CharField(max_length=500)
    reason = models.TextField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
class AbuseReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('spam', 'Spam'),
        ('malware', 'Malware'),
        ('inappropriate', 'Inappropriate Content'),
        ('copyright', 'Copyright Violation'),
    ]
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    url = models.URLField()
    description = models.TextField()
    reporter_email = models.EmailField(blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('investigating', 'Investigating'), ('resolved', 'Resolved')])
    
class SpamDetectionRule(models.Model):
    name = models.CharField(max_length=100)
    pattern_type = models.CharField(max_length=50, choices=[('regex', 'Regex'), ('keyword', 'Keyword'), ('ml', 'Machine Learning')])
    pattern = models.TextField()
    confidence_threshold = models.FloatField(default=0.8)
    action = models.CharField(max_length=20, choices=[('block', 'Block'), ('flag', 'Flag'), ('demote', 'Demote')])