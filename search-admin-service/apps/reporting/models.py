# models.py
class ReportSchedule(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    recipients = models.JSONField()  # Liste d'emails
    report_config = models.JSONField()  # Configuration du rapport
    is_active = models.BooleanField(default=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    
class AlertRule(models.Model):
    name = models.CharField(max_length=100)
    metric = models.CharField(max_length=100)  # Ex: 'response_time', 'error_rate'
    condition = models.CharField(max_length=10, choices=[('gt', 'Greater Than'), ('lt', 'Less Than'), ('eq', 'Equal')])
    threshold = models.FloatField()
    duration = models.IntegerField()  # Durée en minutes pour déclencher l'alerte
    severity = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    is_active = models.BooleanField(default=True)
    
class GeneratedReport(models.Model):
    schedule = models.ForeignKey(ReportSchedule, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    file_path = models.CharField(max_length=500, blank=True)
    file_format = models.CharField(max_length=10, choices=[('pdf', 'PDF'), ('csv', 'CSV'), ('json', 'JSON')])