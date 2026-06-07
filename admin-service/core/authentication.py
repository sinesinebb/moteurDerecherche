import jwt
from django.conf import settings
from rest_framework import authentication, exceptions

class InternalServiceAuthentication(authentication.BaseAuthentication):
    """
    Authentification simple pour les appels internes via un token partagé.
    À adapter selon votre mécanisme JWT.
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        token = auth_header[7:]
        try:
            # Vérifier le token avec la clé publique ou symétrique
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            # On considère que le payload contient l'ID utilisateur et le rôle
            user_id = payload.get('user_id')
            role = payload.get('role')
            if role != 'admin':
                raise exceptions.AuthenticationFailed('Admin privileges required')
            # On retourne un tuple (user, token) – user peut être un simple objet
            user = type('User', (), {'id': user_id, 'is_admin': True})()
            return (user, token)
        except jwt.PyJWTError:
            raise exceptions.AuthenticationFailed('Invalid token')