
# user-service/apps/user/services.py
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import UserSession
import json
import logging
import redis
from django.conf import settings


class UserService:
    """
    Service pour la gestion des utilisateurs.
    """
    
    @staticmethod
    def create_user_session(user, request, expires_hours=24):
        """
        Crée une nouvelle session utilisateur.
        """
        session_token = str(uuid.uuid4())
        
        # Récupérer l'adresse IP et l'user agent
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Calculer la date d'expiration
        expires_at = timezone.now() + timedelta(hours=expires_hours)
        
        # Créer la session
        session = UserSession.objects.create(
            user=user,
            token=session_token,
            ip_address=ip,
            user_agent=user_agent,
            expires_at=expires_at
        )
        
        return session
    
    @staticmethod
    def invalidate_all_sessions(user):
        """
        Invalide toutes les sessions d'un utilisateur.
        """
        UserSession.objects.filter(user=user, is_valid=True).update(is_valid=False)
    
    @staticmethod
    def get_active_sessions(user):
        """
        Récupère toutes les sessions actives d'un utilisateur.
        """
        return UserSession.objects.filter(
            user=user,
            is_valid=True,
            expires_at__gt=timezone.now()
        )
    
    @staticmethod
    def clean_expired_sessions():
        """
        Nettoie les sessions expirées.
        """
        expired_sessions = UserSession.objects.filter(
            expires_at__lte=timezone.now(),
            is_valid=True
        )
        expired_sessions.update(is_valid=False)
        
        return expired_sessions.count()
    
    @staticmethod
    def create_user_from_data(user_data):
        """
        Crée un utilisateur avec validation des données.
        """
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        # Valider le mot de passe
        password = user_data.pop('password', None)
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValueError({'password': list(e.messages)})
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            **user_data,
            password=password
        )
        
        return user
    
    @staticmethod
    def generate_password_reset_token(user):
        """
        Génère un token pour la réinitialisation du mot de passe.
        """
        import secrets
        token = secrets.token_urlsafe(32)
        
        # Stocker le token dans Redis avec une expiration de 1 heure
        from django.core.cache import cache
        cache_key = f'password_reset:{user.id}:{token}'
        cache.set(cache_key, user.id, timeout=3600)
        
        return token
    
    @staticmethod
    def validate_password_reset_token(user_id, token):
        """
        Valide un token de réinitialisation de mot de passe.
        """
        from django.core.cache import cache
        cache_key = f'password_reset:{user_id}:{token}'
        return cache.get(cache_key) == user_id
    

logger = logging.getLogger(__name__)

def publish_user_event(event_type: str, user_data: dict):
    """Publie un événement utilisateur sur Redis Pub/Sub."""
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        message = {"type": event_type, "user": user_data}
        r.publish("user_events", json.dumps(message))
        logger.info(f"Published {event_type} event for user {user_data.get('id')}")
    except Exception as e:
        logger.error(f"Failed to publish user event: {e}")