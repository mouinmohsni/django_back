# users/serializers.py (CORRIGÉ - FINAL)
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from companies.models import Company
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
    # Champ virtuel pour recevoir les informations de l'entreprise lors de l'inscription
    company_info = serializers.JSONField(required=False, write_only=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
            'type',
            'company',
            'avatar',
            'preferences',
            'is_staff',
            'company_info'
        ]
        read_only_fields = ['company', 'is_staff']

    def create(self, validated_data):
        # 1. Extraire les données de l'entreprise si elles existent
        company_info = validated_data.pop('company_info', None)
        user_type = validated_data.get('type', 'personal')

        # 2. Utiliser create_user pour gérer automatiquement le hachage du mot de passe
        # On extrait le mot de passe pour le passer séparément si nécessaire,
        # mais create_user s'en occupe très bien.
        user = User.objects.create_user(**validated_data)

        # 3. Logique spécifique pour le type BUSINESS
        if user_type == 'business' and company_info:
            try:
                # Création de l'entreprise avec les données fournies par le frontend
                new_company = Company.objects.create(
                    name=company_info.get('name', f"Entreprise de {user.username}"),
                    address=company_info.get('address', ''),
                    phone_number=company_info.get('phone_number', ''),
                    description=company_info.get('description', '')
                )
                # Lier l'entreprise à l'utilisateur
                user.company = new_company
                user.save()
            except Exception as e:
                # On log l'erreur mais on ne bloque pas forcément la création de l'utilisateur
                print(f"Erreur lors de la création de l'entreprise : {e}")

        return user

    def update(self, instance, validated_data):
        # Gestion sécurisée du mot de passe lors de la mise à jour
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        return super().update(instance, validated_data)


# --- SERIALIZER SIMPLE POUR LES OBJETS IMBRIQUÉS ---
class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour afficher un utilisateur dans un contexte imbriqué
    (par exemple, l'instructor d'une activité).
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'type')  # ✅ AJOUT
        read_only_fields = fields


# --- SERIALIZER DE MISE À JOUR ---
class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour mettre à jour le profil d'un utilisateur.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'preferences', 'avatar']  # ✅ AJOUT
