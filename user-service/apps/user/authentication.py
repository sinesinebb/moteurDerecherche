from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.utils import timezone
import jwt
from django.conf import settings


User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    Authentification personnalisée avec JWT.
    """
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        try:
            # Format: "Bearer <token>"
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
            
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Token invalide')
            
            user = User.objects.get(id=user_id)
            
            # Vérifier si l'utilisateur est actif
            if not user.is_active:
                raise AuthenticationFailed('Utilisateur désactivé')
            
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expiré')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token invalide')
        except User.DoesNotExist:
            raise AuthenticationFailed('Utilisateur non trouvé')