# user-service/apps/user/views.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.utils import timezone
from datetime import timedelta
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.storage import default_storage
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import random
import string
import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from .services import publish_user_event


from .models import User, UserSession
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, UserSessionSerializer, LoginSerializer,
    AvatarUploadSerializer,
    EmailVerificationRequestSerializer, EmailVerificationCodeSerializer,
    PasswordResetRequestSerializer, PasswordResetSerializer,
    GoogleLoginSerializer
)
from .permissions import IsOwnerOrAdmin
from .services import UserService

# Pour Google auth
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny] 

    @action(detail=False, methods=['post'], serializer_class=LoginSerializer)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        refresh['is_superuser'] = user.is_superuser

        session = UserService.create_user_session(user, request)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'session_id': str(session.id),
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        session_id = request.data.get('session_id')
        if session_id:
            try:
                session = UserSession.objects.get(id=session_id, user=request.user)
                session.is_valid = False
                session.save()
            except UserSession.DoesNotExist:
                pass
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return Response({"message": "Déconnexion réussie"})

    @action(detail=False, methods=['post'], serializer_class=UserCreateSerializer)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        from apps.search_history.models import UserPreference
        UserPreference.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        refresh['is_superuser'] = user.is_superuser
        
        # Publier événement création
        user_data = UserSerializer(user).data
        print("🔵 [USER-SERVICE] About to publish user.created for", user_data['email'])
        publish_user_event("user.created", user_data)
        print("🟢 [USER-SERVICE] publish_user_event called")
        
        return Response({
            'user': user_data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

    # ========== NOUVELLES ACTIONS ==========
    
    @action(detail=False, methods=['post'], serializer_class=EmailVerificationRequestSerializer)
    def send_verification_email(self, request):
        """Envoie un code de vérification par email."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        if user.email_verified:
            return Response({'message': 'Email déjà vérifié'}, status=status.HTTP_200_OK)

        # Générer un code à 6 chiffres
        code = ''.join(random.choices(string.digits, k=6))
        cache_key = f'email_verify:{user.id}'
        cache.set(cache_key, code, timeout=300)  # 5 minutes

        # Envoyer l'email
        send_mail(
            subject='Vérification de votre email - Search.dev',
            message=f'Votre code de vérification est : {code}\n\nCe code est valable 5 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({'message': 'Code envoyé par email'})

    @action(detail=False, methods=['post'], serializer_class=EmailVerificationCodeSerializer)
    def verify_email(self, request):
        """Valide le code de vérification."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        cache_key = f'email_verify:{user.id}'
        stored_code = cache.get(cache_key)
        if stored_code is None or stored_code != code:
            return Response({'error': 'Code invalide ou expiré'}, status=status.HTTP_400_BAD_REQUEST)

        user.email_verified = True
        user.save(update_fields=['email_verified'])
        cache.delete(cache_key)

        return Response({'message': 'Email vérifié avec succès'})

    @action(detail=False, methods=['post'], serializer_class=PasswordResetRequestSerializer)
    def password_reset_request(self, request):
        """Demande de réinitialisation de mot de passe (envoi d'un code)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Ne pas révéler que l'utilisateur n'existe pas pour des raisons de sécurité
            return Response({'message': 'Si cet email existe, un code vous a été envoyé.'})

        code = ''.join(random.choices(string.digits, k=6))
        cache_key = f'password_reset:{email}'
        cache.set(cache_key, code, timeout=3600)  # 1 heure

        send_mail(
            subject='Réinitialisation de votre mot de passe - Search.dev',
            message=f'Votre code de réinitialisation est : {code}\n\nCe code est valable 1 heure.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({'message': 'Si cet email existe, un code vous a été envoyé.'})

    @action(detail=False, methods=['post'], serializer_class=PasswordResetSerializer)
    def password_reset(self, request):
        """Réinitialise le mot de passe avec le code reçu."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        cache_key = f'password_reset:{email}'
        stored_code = cache.get(cache_key)
        if stored_code is None or stored_code != code:
            return Response({'error': 'Code invalide ou expiré'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        cache.delete(cache_key)

        # Optionnel : invalider toutes les sessions existantes
        UserSession.objects.filter(user=user).update(is_valid=False)

        return Response({'message': 'Mot de passe réinitialisé avec succès'})

    @action(detail=False, methods=['post'], serializer_class=GoogleLoginSerializer)
    def google_login(self, request):
        """Connexion avec Google OAuth2."""
        if not GOOGLE_AUTH_AVAILABLE:
            return Response({'error': 'Service Google non disponible'}, status=status.HTTP_501_NOT_IMPLEMENTED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id_token_str = serializer.validated_data['id_token']

        try:
            # Vérifier le token avec Google
            CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
            if not CLIENT_ID:
                return Response({'error': 'Configuration Google manquante'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            request_adapter = google_requests.Request()
            info = id_token.verify_oauth2_token(id_token_str, request_adapter, CLIENT_ID)

            # Vérifier l'audience
            if info.get('aud') != CLIENT_ID:
                return Response({'error': 'Token invalide'}, status=status.HTTP_400_BAD_REQUEST)

            email = info.get('email')
            if not email:
                return Response({'error': 'Email non fourni par Google'}, status=status.HTTP_400_BAD_REQUEST)

            name = info.get('name', '')
            first_name = name.split()[0] if name else ''
            last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''

        except Exception as e:
            return Response({'error': f'Échec de validation Google: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer ou créer l'utilisateur
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': first_name,
                'last_name': last_name,
                'email_verified': True,  # Google a déjà vérifié l'email
                'is_active': True,
            }
        )
        if not created:
            # Mettre à jour l'email_verified si ce n'était pas déjà le cas
            if not user.email_verified:
                user.email_verified = True
                user.save(update_fields=['email_verified'])
            # Optionnel : mettre à jour le nom s'il est vide
            if not user.first_name and first_name:
                user.first_name = first_name
                user.last_name = last_name
                user.save(update_fields=['first_name', 'last_name'])

        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        refresh['is_superuser'] = user.is_superuser

        # On créer une session (comme dans login)
        session = UserService.create_user_session(user, request)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'session_id': str(session.id),
        })


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_queryset(self):
        # Retourne un queryset frais à chaque requête
        return User.objects.all().order_by('-date_joined')
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'], serializer_class=UserUpdateSerializer)
    def update_profile(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
    @action(detail=False, methods=['post'], serializer_class=ChangePasswordSerializer)
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({"message": "Mot de passe modifié avec succès"})
    
    @action(detail=False, methods=['get'])
    def sessions(self, request):
        sessions = UserSession.objects.filter(user=request.user, is_valid=True)
        serializer = UserSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def invalidate_session(self, request):
        session_id = request.data.get('session_id')
        if not session_id:
            return Response(
                {"error": "session_id requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = UserSession.objects.get(id=session_id, user=request.user)
            session.is_valid = False
            session.save()
            return Response({"message": "Session invalidée"})
        except UserSession.DoesNotExist:
            return Response(
                {"error": "Session non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], serializer_class=AvatarUploadSerializer,
            permission_classes=[IsAuthenticated])
    def upload_avatar(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        avatar_file = serializer.validated_data['avatar']
        user = request.user
        
        # Supprimer l'ancien avatar si présent
        if user.avatar:
            old_avatar = user.avatar
            user.avatar = None
            user.save()
            if old_avatar and default_storage.exists(old_avatar.name):
                default_storage.delete(old_avatar.name)
        
        # Enregistrer le nouveau
        user.avatar.save(avatar_file.name, avatar_file, save=True)
        
        return Response({
            'avatar': user.avatar.url if user.avatar else None,
            'message': 'Avatar mis à jour avec succès'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_account(self, request):
        password = request.data.get('password')
        if not password:
            return Response(
                {'error': 'Le mot de passe est requis pour confirmer la suppression'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        if not user.check_password(password):
            return Response(
                {'error': 'Mot de passe incorrect'},
                status=status.HTTP_403_FORBIDDEN
            )
        
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user_data = UserSerializer(user).data
        print(f"🔴 [USER-SERVICE] About to publish user.deleted for {user_data['email']}")
        publish_user_event("user.deleted", user_data)
        self.perform_destroy(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        user_data = UserSerializer(user).data
        print("🔴 [USER-SERVICE] About to publish user.deleted for", user_data['email'])
        publish_user_event("user.deleted", user_data)
        UserSession.objects.filter(user=user).delete()
        user.delete()
        
        return Response(
            {'message': 'Compte supprimé avec succès'},
            status=status.HTTP_204_NO_CONTENT
        )


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            session_id = request.data.get('session_id')
            if session_id:
                try:
                    session = UserSession.objects.get(id=session_id, user=request.user)
                    # Ici, vous pourriez avoir une méthode renew dans le modèle
                    # Exemple : session.renew()
                    session.expires_at = timezone.now() + timedelta(hours=24)
                    session.save()
                except UserSession.DoesNotExist:
                    pass
        
        return response