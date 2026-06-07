from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class ServiceException(Exception):
    """Exception de base pour les services."""
    pass


class UserNotFoundException(ServiceException):
    """Exception levée quand un utilisateur n'est pas trouvé."""
    pass


class InvalidCredentialsException(ServiceException):
    """Exception levée quand les identifiants sont invalides."""
    pass


class TokenExpiredException(ServiceException):
    """Exception levée quand un token JWT est expiré."""
    pass


class PermissionDeniedException(ServiceException):
    """Exception levée quand l'utilisateur n'a pas les permissions nécessaires."""
    pass


def custom_exception_handler(exc, context):
    """
    Gestionnaire d'exceptions personnalisé pour l'API.
    """
    # Appeler le gestionnaire d'exceptions par défaut
    response = exception_handler(exc, context)
    
    if response is None:
        # Si ce n'est pas une exception DRF, logger et renvoyer une erreur 500
        logger.error(f"Exception non gérée: {exc}", exc_info=True)
        
        if isinstance(exc, ServiceException):
            status_code = status.HTTP_400_BAD_REQUEST
            detail = str(exc)
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            detail = "Une erreur interne est survenue"
        
        response = Response(
            {
                'error': True,
                'message': detail,
                'code': 'internal_error'
            },
            status=status_code
        )
    else:
        # Personnaliser le format de la réponse DRF
        custom_data = {
            'error': True,
            'message': response.data.get('detail', 'Une erreur est survenue'),
            'code': exc.__class__.__name__.lower(),
        }
        
        # Ajouter les erreurs de validation
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_data['validation_errors'] = response.data
        
        response.data = custom_data
    
    return response