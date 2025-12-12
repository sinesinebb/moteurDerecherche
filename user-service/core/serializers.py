from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, UserProfile, BlacklistedToken, SearchHistory, UserSearchPreferences
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_verified', 'preferred_language', 
                 'safe_search', 'results_per_page', 'created_at')

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('bio', 'location', 'last_password_change')

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm')
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value
    
    def validate_password(self, value):
        # Validation de la force du mot de passe
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        # Validation personnalisée
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une minuscule.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        
        return value
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        # Créer le profil utilisateur
        UserProfile.objects.create(user=user)
        # Créer les préférences de recherche par défaut
        UserSearchPreferences.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            try:
                user = User.objects.get(email=email)
                
                # Vérifier si le compte est verrouillé
                if user.is_account_locked():
                    raise serializers.ValidationError("Compte temporairement verrouillé. Réessayez dans 30 minutes.")
                
                user = authenticate(username=email, password=password)
                if user:
                    if user.is_active:
                        user.reset_login_attempts()  # Réinitialiser les tentatives en cas de succès
                        data['user'] = user
                    else:
                        raise serializers.ValidationError("Compte utilisateur désactivé.")
                else:
                    user.increment_login_attempts()  # Incrémenter les tentatives en cas d'échec
                    raise serializers.ValidationError("Email ou mot de passe incorrect.")
            except User.DoesNotExist:
                raise serializers.ValidationError("Email ou mot de passe incorrect.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")
        
        return data

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()
    
    def validate_new_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Les nouveaux mots de passe ne correspondent pas."})
        return data

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['preferred_language', 'safe_search', 'results_per_page']
        read_only_fields = ['id', 'email', 'username']

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'query', 'timestamp', 'results_count', 'search_filters']
        read_only_fields = ['id', 'timestamp', 'user']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name']
        read_only_fields = ['email']  # L'email ne peut pas être modifié

class UserSearchPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSearchPreferences
        fields = ['default_sort', 'default_filters', 'notification_enabled', 'last_updated']
        read_only_fields = ['user', 'last_updated']
