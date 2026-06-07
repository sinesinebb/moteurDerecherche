from django.db import models

class SystemConfiguration(models.Model):
    """Paramètres globaux du moteur"""
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

class AuditLog(models.Model):
    ACTION_TYPES = (
        ('user_update', 'Mise à jour utilisateur'),
        ('config_change', 'Changement configuration'),
        ('index_trigger', 'Déclenchement indexation'),
        ('system_restart', 'Redémarrage service'),
        ('crawler_control', 'Contrôle du crawler'),
    )
    user_id = models.IntegerField(null=True, blank=True)  # ID de l'admin (référence externe)
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    details = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class MetricSnapshot(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    tags = models.JSONField(default=dict)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['name', 'timestamp']),
        ]