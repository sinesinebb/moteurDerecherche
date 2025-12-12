from rest_framework import status, generics, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
import jwt
from django.conf import settings

from django.db import transaction
from .models import SearchHistory

from .models import User, UserProfile, BlacklistedToken
from .serializers import (
    UserSerializer, RegistrationSerializer, LoginSerializer, 
    PasswordChangeSerializer, UserProfileSerializer, UserPreferencesSerializer,
    SearchHistorySerializer  # Maintenant disponible
)
from .authentication import JWTAuthentication
from django.shortcuts import render

from .models import User, UserProfile, BlacklistedToken, UserSession, SearchHistory





@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Générer les tokens JWT
        access_token_payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': timezone.now() + timezone.timedelta(seconds=settings.JWT_CONFIG['ACCESS_TOKEN_LIFETIME']),
            'type': 'access',
            'iat': timezone.now()
        }
        
        refresh_token_payload = {
            'user_id': user.id,
            'exp': timezone.now() + timezone.timedelta(seconds=settings.JWT_CONFIG['REFRESH_TOKEN_LIFETIME']),
            'type': 'refresh',
            'iat': timezone.now()
        }
        
        access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm=settings.JWT_CONFIG['ALGORITHM'])
        refresh_token = jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm=settings.JWT_CONFIG['ALGORITHM'])
        
        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': settings.JWT_CONFIG['ACCESS_TOKEN_LIFETIME'],
            'user': UserSerializer(user).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Déconnexion avec blacklisting du token"""
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(' ')[1]
            # Décoder le token pour obtenir la date d'expiration
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_CONFIG['ALGORITHM']])
            expires_at = timezone.datetime.fromtimestamp(payload['exp'])
            
            # Ajouter le token à la blacklist
            BlacklistedToken.objects.create(token=token, expires_at=expires_at)
            
            # Nettoyer les tokens expirés
            BlacklistedToken.clean_expired_tokens()
            
        except (jwt.InvalidTokenError, IndexError):
            pass
    
    return Response({'message': 'Déconnexion réussie'})

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Rafraîchir le token d'accès"""
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        return Response({'error': 'Refresh token requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.JWT_CONFIG['ALGORITHM']])
        
        if payload.get('type') != 'refresh':
            return Response({'error': 'Type de token invalide'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = payload.get('user_id')
        user = User.objects.get(id=user_id)
        
        # Générer un nouveau token d'accès
        access_token_payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': timezone.now() + timezone.timedelta(seconds=settings.JWT_CONFIG['ACCESS_TOKEN_LIFETIME']),
            'type': 'access',
            'iat': timezone.now()
        }
        
        new_access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm=settings.JWT_CONFIG['ALGORITHM'])
        
        return Response({
            'access_token': new_access_token,
            'expires_in': settings.JWT_CONFIG['ACCESS_TOKEN_LIFETIME']
        })
        
    except jwt.ExpiredSignatureError:
        return Response({'error': 'Refresh token expiré'}, status=status.HTTP_401_UNAUTHORIZED)
    except (jwt.InvalidTokenError, User.DoesNotExist):
        return Response({'error': 'Refresh token invalide'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Obtenir ou mettre à jour le profil utilisateur"""
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Changer le mot de passe"""
    serializer = PasswordChangeSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        
        # Vérifier l'ancien mot de passe
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Mot de passe incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Changer le mot de passe
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Mettre à jour la date de changement de mot de passe
        user.profile.last_password_change = timezone.now()
        user.profile.save()
        
        # Mettre à jour la session pour éviter la déconnexion
        update_session_auth_hash(request, user)
        
        return Response({'message': 'Mot de passe changé avec succès'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_preferences(request):
    """Obtenir les préférences utilisateur pour la recherche"""
    preferences = {
        'preferred_language': request.user.preferred_language,
        'safe_search': request.user.safe_search,
        'results_per_page': request.user.results_per_page,
    }
    return Response(preferences)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_preferences(request):
    """Mettre à jour les préférences utilisateur"""
    serializer = UserPreferencesSerializer(request.user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Préférences mises à jour avec succès',
            'preferences': serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_search_history(request):
    """Ajouter une recherche à l'historique"""
    try:
        data = request.data.copy()
        
        # Créer une entrée dans l'historique
        search_entry = SearchHistory.objects.create(
            user=request.user,
            query=data.get('query', ''),
            results_count=data.get('results_count', 0),
            search_filters=data.get('filters', {})
        )
        
        # Limiter l'historique à 100 entrées par utilisateur
        user_history = SearchHistory.objects.filter(user=request.user)
        if user_history.count() > 100:
            # Supprimer les entrées les plus anciennes
            ids_to_delete = user_history.order_by('timestamp').values_list('id', flat=True)[:user_history.count()-100]
            SearchHistory.objects.filter(id__in=list(ids_to_delete)).delete()
        
        return Response({
            'message': 'Recherche ajoutée à l\'historique',
            'id': search_entry.id,
            'timestamp': search_entry.timestamp
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_search_history(request):
    """Récupérer l'historique de recherche"""
    try:
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        
        history = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')
        
        total = history.count()
        entries = history[offset:offset + limit]
        
        serializer = SearchHistorySerializer(entries, many=True)
        
        return Response({
            'total': total,
            'offset': offset,
            'limit': limit,
            'history': serializer.data
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_search_history(request):
    """Effacer tout l'historique de recherche"""
    try:
        deleted_count, _ = SearchHistory.objects.filter(user=request.user).delete()
        
        return Response({
            'message': f'Historique effacé ({deleted_count} entrées supprimées)'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):
    """Mettre à jour le mot de passe"""
    serializer = PasswordChangeSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user
        
        # Vérifier l'ancien mot de passe
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Mot de passe incorrect'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le mot de passe
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Mettre à jour la date de changement
        if hasattr(user, 'profile'):
            user.profile.last_password_change = timezone.now()
            user.profile.save()
        
        # Invalider les tokens existants
        BlacklistedToken.clean_expired_tokens()
        
        return Response({
            'message': 'Mot de passe mis à jour avec succès'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_preferences(request):
    """Mettre à jour les préférences utilisateur"""
    user = request.user
    
    # Champs autorisés à être mis à jour
    allowed_fields = ['preferred_language', 'safe_search', 'results_per_page']
    
    try:
        data = request.data
        
        # Valider et mettre à jour chaque champ
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
        
        # Mettre à jour le profil
        if hasattr(user, 'profile'):
            user.profile.last_password_change = timezone.now()
            user.profile.save()
        
        return Response({
            'message': 'Préférences mises à jour avec succès',
            'preferences': {
                'preferred_language': user.preferred_language,
                'safe_search': user.safe_search,
                'results_per_page': user.results_per_page
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la mise à jour: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_search_history(request):
    """Ajouter une recherche à l'historique"""
    try:
        from .models import SearchHistory  # Import ici pour éviter les problèmes circulaires
        
        data = request.data
        
        # Créer l'entrée d'historique
        search_entry = SearchHistory.objects.create(
            user=request.user,
            query=data.get('query', ''),
            results_count=data.get('results_count', 0),
            search_filters=data.get('filters', {})
        )
        
        # Limiter à 100 entrées max
        user_history = SearchHistory.objects.filter(user=request.user)
        if user_history.count() > 100:
            oldest_entries = user_history.order_by('timestamp')[:user_history.count() - 100]
            SearchHistory.objects.filter(id__in=[e.id for e in oldest_entries]).delete()
        
        return Response({
            'message': 'Recherche ajoutée à l\'historique',
            'id': search_entry.id,
            'timestamp': search_entry.timestamp
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Erreur: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_search_history(request):
    """Récupérer l'historique de recherche"""
    try:
        from .models import SearchHistory
        
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        history_queryset = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')
        total = history_queryset.count()
        
        entries = history_queryset[offset:offset + limit]
        
        history_data = []
        for entry in entries:
            history_data.append({
                'id': entry.id,
                'query': entry.query,
                'timestamp': entry.timestamp.isoformat(),
                'results_count': entry.results_count,
                'search_filters': entry.search_filters
            })
        
        return Response({
            'total': total,
            'offset': offset,
            'limit': limit,
            'history': history_data
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_search_history(request):
    """Effacer tout l'historique de recherche"""
    try:
        from .models import SearchHistory
        
        deleted_count = SearchHistory.objects.filter(user=request.user).delete()[0]
        
        return Response({
            'message': f'Historique effacé ({deleted_count} entrées supprimées)'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )