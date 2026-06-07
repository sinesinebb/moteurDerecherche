import jwt
import logging
from django.conf import settings
from rest_framework import authentication, exceptions

logger = logging.getLogger(__name__)

class StatelessJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                return None
        except ValueError:
            return None

        try:
            payload = jwt.decode(
                token,
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=[settings.SIMPLE_JWT['ALGORITHM']]
            )
            logger.info(f"JWT payload: is_superuser={payload.get('is_superuser')}")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expiré')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Token invalide')

        user = type('User', (), {
            'is_authenticated': True,
            'id': payload.get('user_id'),
            'is_superuser': payload.get('is_superuser', False),
            'is_staff': payload.get('is_superuser', False),
            'role': 'admin' if payload.get('is_superuser') else 'user',
            'email': payload.get('email', ''),
            'has_perm': lambda self, perm, obj=None: payload.get('is_superuser', False),
            'has_module_perms': lambda self, app_label: payload.get('is_superuser', False),
        })()
        return (user, token)