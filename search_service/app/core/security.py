# app/core/security.py
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, List, Callable
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
import hashlib
import hmac
from core.config import settings
from services.user_client import UserServiceClient
import logging

logger = logging.getLogger(__name__)

# Models pour la sécurité
class TokenPayload(BaseModel):
    """Payload du token JWT"""
    sub: str  # user_id
    exp: datetime
    iat: datetime
    type: str = "access"  # access, refresh, service
    scopes: List[str] = []
    service: Optional[str] = None

class UserContext(BaseModel):
    """Contexte utilisateur authentifié"""
    user_id: str
    username: str
    email: str
    roles: List[str]
    permissions: List[str]
    is_active: bool
    is_verified: bool

class ServiceContext(BaseModel):
    """Contexte service authentifié"""
    service_name: str
    service_id: str
    permissions: List[str]

# Security instances
security = HTTPBearer(auto_error=False)
service_security = HTTPBearer(auto_error=False)

class SecurityManager:
    """Gestionnaire de sécurité avancé"""
    
    def __init__(self):
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.service_tokens = self._load_service_tokens()
    
    def _load_service_tokens(self) -> Dict[str, str]:
        """Charge les tokens de service depuis l'environnement"""
        return {
            "user-service": settings.SECRET_KEY + "user",
            "indexing-service": settings.SECRET_KEY + "indexing",
            "pagerank-service": settings.SECRET_KEY + "pagerank",
            "admin-service": settings.SECRET_KEY + "admin"
        }
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token JWT d'accès"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        return jwt.encode(to_encode, self.jwt_secret, algorithm=self.algorithm)
    
    def create_service_token(self, service_name: str) -> str:
        """Crée un token pour l'authentification inter-services"""
        payload = {
            "sub": service_name,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
            "type": "service",
            "service": service_name,
            "scopes": ["service:internal"]
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)
    
    def verify_token(self, token: str, expected_type: str = "access") -> TokenPayload:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.algorithm]
            )
            
            token_payload = TokenPayload(**payload)
            
            # Vérifier le type de token
            if token_payload.type != expected_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected: {expected_type}"
                )
            
            # Vérifier l'expiration
            if token_payload.exp < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            
            return token_payload
            
        except PyJWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    def verify_service_token(self, token: str, required_permissions: List[str] = None) -> ServiceContext:
        """Vérifie un token de service"""
        token_payload = self.verify_token(token, "service")
        
        if not token_payload.service:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service token"
            )
        
        # Vérifier les permissions
        if required_permissions:
            missing_permissions = set(required_permissions) - set(token_payload.scopes)
            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permissions: {missing_permissions}"
                )
        
        return ServiceContext(
            service_name=token_payload.service,
            service_id=token_payload.sub,
            permissions=token_payload.scopes
        )
    
    def hash_password(self, password: str) -> str:
        """Hash un mot de passe (pour référence)"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            settings.SECRET_KEY.encode('utf-8'),
            100000
        ).hex()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Vérifie un mot de passe contre son hash"""
        return hmac.compare_digest(
            self.hash_password(password),
            hashed
        )
    
    def generate_api_key(self, user_id: str) -> str:
        """Génère une clé API pour un utilisateur"""
        data = f"{user_id}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(
            f"{data}:{settings.SECRET_KEY}".encode()
        ).hexdigest()

# Instance globale
security_manager = SecurityManager()

# Dependencies
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_client: UserServiceClient = Depends()
) -> UserContext:
    """Dépendance pour récupérer l'utilisateur courant"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Vérifier le token localement d'abord
        token_payload = security_manager.verify_token(token)
        
        # Récupérer les infos utilisateur depuis le User Service
        user_data = await user_client.get_user_profile(token_payload.sub)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return UserContext(
            user_id=user_data.id,
            username=user_data.username,
            email=user_data.email,
            roles=user_data.roles or [],
            permissions=user_data.permissions or [],
            is_active=user_data.is_active,
            is_verified=user_data.is_verified
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def get_current_service(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(service_security),
) -> ServiceContext:
    """Dépendance pour l'authentification inter-services"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Service authentication required",
        )
    
    token = credentials.credentials
    return security_manager.verify_service_token(token)

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_client: UserServiceClient = Depends()
) -> Optional[UserContext]:
    """Version optionnelle qui ne lève pas d'exception si non authentifié"""
    try:
        return await get_current_user(credentials, user_client)
    except HTTPException:
        return None

# Permission checks
def require_permission(permission: str):
    """Décorateur pour vérifier les permissions"""
    def permission_checker(user: UserContext = Depends(get_current_user)):
        if permission not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        return user
    return permission_checker

def require_role(role: str):
    """Décorateur pour vérifier les rôles"""
    def role_checker(user: UserContext = Depends(get_current_user)):
        if role not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role}"
            )
        return user
    return role_checker

# Rate limiting
class RateLimiter:
    """Limiteur de taux avancé"""
    
    def __init__(self, requests: int, window: int):
        self.requests = requests
        self.window = window
        self.requests_log = {}
    
    async def __call__(self, request: Request):
        """Implémentation du rate limiting"""
        client_ip = request.client.host
        current_time = datetime.utcnow().timestamp()
        
        # Nettoyer les anciennes entrées
        self._clean_old_entries(current_time)
        
        # Vérifier le taux
        if client_ip in self.requests_log:
            if len(self.requests_log[client_ip]) >= self.requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            self.requests_log[client_ip].append(current_time)
        else:
            self.requests_log[client_ip] = [current_time]
    
    def _clean_old_entries(self, current_time: float):
        """Nettoie les entrées plus anciennes que la fenêtre"""
        cutoff = current_time - self.window
        for ip in list(self.requests_log.keys()):
            self.requests_log[ip] = [
                t for t in self.requests_log[ip] if t > cutoff
            ]
            if not self.requests_log[ip]:
                del self.requests_log[ip]

# Instance de rate limiting globale
rate_limiter = RateLimiter(
    requests=settings.RATE_LIMIT_REQUESTS,
    window=settings.RATE_LIMIT_WINDOW
)