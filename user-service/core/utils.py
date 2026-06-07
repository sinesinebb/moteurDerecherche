import json
import hashlib
import uuid
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone


class CacheManager:
    """
    Gestionnaire de cache avec des méthodes utilitaires.
    """
    
    @staticmethod
    def generate_cache_key(prefix, *args):
        """
        Génère une clé de cache unique.
        """
        key_string = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @staticmethod
    def get_or_set(key, callback, timeout=300):
        """
        Récupère une valeur du cache ou l'ajoute si elle n'existe pas.
        """
        value = cache.get(key)
        if value is None:
            value = callback()
            cache.set(key, value, timeout)
        return value
    
    @staticmethod
    def invalidate_pattern(pattern):
        """
        Invalide toutes les clés correspondant à un pattern.
        """
        cache.delete_pattern(pattern)


class JSONEncoder(DjangoJSONEncoder):
    """
    Encodeur JSON personnalisé pour Django.
    """
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


def format_error_response(message, code=None, details=None):
    """
    Formate une réponse d'erreur standardisée.
    """
    response = {
        'success': False,
        'message': message,
        'timestamp': timezone.now().isoformat(),
    }
    
    if code:
        response['code'] = code
    
    if details:
        response['details'] = details
    
    return response


def format_success_response(data=None, message=None):
    """
    Formate une réponse de succès standardisée.
    """
    response = {
        'success': True,
        'timestamp': timezone.now().isoformat(),
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    return response


def validate_email(email):
    """
    Valide le format d'un email.
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def get_client_ip(request):
    """
    Récupère l'adresse IP du client.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def rate_limit(key, limit, period):
    """
    Implémente une limitation de taux.
    
    Args:
        key: Clé unique pour la limitation
        limit: Nombre maximum de requêtes
        period: Période en secondes
    
    Returns:
        bool: True si la requête est autorisée, False sinon
    """
    cache_key = f'rate_limit:{key}'
    
    # Récupérer le compteur actuel
    current = cache.get(cache_key)
    
    if current is None:
        # Première requête
        cache.set(cache_key, 1, period)
        return True
    
    if current >= limit:
        # Limite atteinte
        return False
    
    # Incrémenter le compteur
    cache.incr(cache_key)
    return True