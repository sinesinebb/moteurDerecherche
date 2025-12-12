import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from .models import BlacklistedToken

User = get_user_model()

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
            
        try:
            # Format: "Bearer <token>"
            token = auth_header.split(' ')[1]
            
            # Vérifier si le token est blacklisté
            if BlacklistedToken.objects.filter(token=token).exists():
                raise AuthenticationFailed('Token has been blacklisted')
            
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_CONFIG['ALGORITHM']])
            
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Invalid token')
                
            user = User.objects.get(id=user_id)
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')