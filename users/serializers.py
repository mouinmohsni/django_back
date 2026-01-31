# users/serializers.py (CORRIGÉ - FINAL)
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from users.models import CustomUser

User = get_user_model()

# --- SERIALIZER D'INSCRIPTION PERSONNEL ---
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    preferences = serializers.JSONField(required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'preferences')

    def create(self, validated_data):
        password = validated_data.pop('password')
        preferences = validated_data.pop('preferences', {})
        user = User.objects.create(
            **validated_data,
            type=User.USER_TYPE_PERSONAL
        )
        user.set_password(password)
        user.preferences = preferences
        user.save()
        return user


# --- SERIALIZER D'INSCRIPTION BUSINESS ---
class BusinessRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    preferences = serializers.JSONField(required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'preferences')

    def create(self, validated_data):
        password = validated_data.pop('password')
        preferences = validated_data.pop('preferences', {})
        user = User.objects.create(
            **validated_data,
            type=User.USER_TYPE_BUSINESS
        )
        user.set_password(password)
        user.preferences = preferences
        user.save()
        return user


# --- SERIALIZER PRINCIPAL UTILISATEUR ---
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour afficher les informations d'un utilisateur.
    N'inclut PAS la liste des activités pour éviter l'importation circulaire.
    Utiliser l'endpoint /api/users/{id}/activities/ pour récupérer les activités.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'type', 'preferences', 'avatar', 'is_staff', 'company')
        read_only_fields = fields


# --- SERIALIZER SIMPLE POUR LES OBJETS IMBRIQUÉS ---
class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour afficher un utilisateur dans un contexte imbriqué
    (par exemple, l'instructor d'une activité).
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'avatar', 'type')
        read_only_fields = fields


# --- SERIALIZER DE MISE À JOUR ---
class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour mettre à jour le profil d'un utilisateur.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'preferences', 'avatar']
