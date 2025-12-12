from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Préférences de recherche
    preferred_language = models.CharField(max_length=10, default='fr')
    safe_search = models.BooleanField(default=True)
    results_per_page = models.IntegerField(default=10)
    
    # Sécurité
    login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def is_account_locked(self):
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        # Déverrouiller si la période de verrouillage est passée
        if self.locked_until and timezone.now() >= self.locked_until:
            self.locked_until = None
            self.login_attempts = 0
            self.save()
        return False
    
    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= 5:  # Verrouiller après 5 tentatives
            self.locked_until = timezone.now() + timedelta(minutes=30)
        self.save()
    
    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None
        self.save()
    
    def __str__(self):
        return self.email

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    last_password_change = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Profile of {self.user.email}"

class BlacklistedToken(models.Model):
    token = models.TextField(unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        indexes = [
            models.Index(fields=['expires_at']),
        ]
    
    @classmethod
    def clean_expired_tokens(cls):
        """Nettoyer les tokens expirés"""
        cls.objects.filter(expires_at__lte=timezone.now()).delete()

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'expires_at']),
        ]



class SearchHistory(models.Model):
    """Modèle pour l'historique de recherche utilisateur"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    results_count = models.IntegerField(default=0)
    search_filters = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Historique de recherche'
        verbose_name_plural = 'Historiques de recherche'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.query[:50]}"

class UserSearchPreferences(models.Model):
    """Préférences de recherche persistantes"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='search_preferences')
    default_sort = models.CharField(max_length=50, default='relevance')
    default_filters = models.JSONField(default=dict, blank=True)
    notification_enabled = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Préférences de {self.user.email}"

