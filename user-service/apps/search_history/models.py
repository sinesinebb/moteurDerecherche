# user-service/apps/search_history/models.py
from django.db import models
from django.utils import timezone
import uuid

class SearchHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='search_history')
    query = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.query[:50]}..."


class SearchResult(models.Model):
    """Résultat individuel d'une recherche"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_history = models.ForeignKey(
        SearchHistory, 
        on_delete=models.CASCADE, 
        related_name='results'
    )
    document_id = models.CharField(max_length=255)
    title = models.TextField()
    url = models.URLField(max_length=500)
    snippet = models.TextField()
    relevance_score = models.FloatField(default=0.0)
    pagerank_score = models.FloatField(default=0.0)
    final_score = models.FloatField(default=0.0)
    position = models.IntegerField()
    clicked = models.BooleanField(default=False)
    click_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'search_result'
        unique_together = [['search_history', 'document_id']]
    
    def __str__(self):
        return f"{self.document_id} - {self.title[:50]}"

class UserPreference(models.Model):
    """Préférences utilisateur pour la recherche"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'user.User', 
        on_delete=models.CASCADE, 
        related_name='preferences'
    )
    theme = models.CharField(max_length=10, default='auto')
    language = models.CharField(max_length=2, default='fr')
    results_per_page = models.IntegerField(default=10)
    enable_notifications = models.BooleanField(default=True)
    save_search_history = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preference'
    
    def __str__(self):
        return f"Préférences de {self.user.username}"