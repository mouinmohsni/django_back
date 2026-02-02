# users/serializers.py

from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction  # Important pour des créations atomiques

from companies.models import Company

User = get_user_model()

# ===================================================================
# == SERIALIZER DE LECTURE (POUR AFFICHER LES UTILISATEURS)
# ===================================================================
class UserReadSerializer(serializers.ModelSerializer):
    """
    Serializer pour AFFICHER les informations d'un utilisateur.
    Il n'expose JAMAIS le mot de passe.
    """
    # On importe le serializer de Company ici pour l'affichage
    from companies.serializers import SimpleCompanySerializer
    company = SimpleCompanySerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'type', 'company', 'avatar', 'preferences', 'is_staff'
        ]
        # Tous les champs sont en lecture seule par défaut dans ce serializer.
        read_only_fields = fields

# ===================================================================
# == SERIALIZER DE CRÉATION (POUR L'INSCRIPTION)
# ===================================================================
class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour CRÉER un nouvel utilisateur (inscription).
    Gère la création conditionnelle de l'entreprise pour les comptes 'business'.
    """
    # On redéfinit le champ 'password' pour s'assurer qu'il est en écriture seule
    # et qu'il utilise les validateurs de mot de passe de Django.
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    # Champ virtuel pour recevoir les données de l'entreprise lors de l'inscription.
    # Il n'est pas lié à un champ du modèle User.
    company_info = serializers.JSONField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'first_name', 'last_name',
            'type', 'preferences', 'company_info'
        ]
        # 'id' est le seul champ qui sera lu après la création.
        read_only_fields = ['id']

    def validate_type(self, value):
        """
        Valide que le type d'utilisateur fourni est l'un des choix autorisés.
        """
        allowed_types = [choice[0] for choice in User.USER_TYPE_CHOICES]
        if value not in allowed_types:
            raise serializers.ValidationError(f"Le type '{value}' n'est pas valide.")
        return value

    def create(self, validated_data):
        """
        Crée l'utilisateur et, si c'est un 'business', son entreprise dans une transaction.
        C'est "tout ou rien" : si la création de l'entreprise échoue, l'utilisateur n'est pas créé.
        """
        company_info = validated_data.pop('company_info', None)
        user_type = validated_data.get('type', User.USER_TYPE_PERSONAL)

        # On utilise une transaction pour garantir l'intégrité des données.
        try:
            with transaction.atomic():
                # On utilise create_user pour hacher automatiquement le mot de passe.
                user = User.objects.create_user(**validated_data)

                # Si c'est un propriétaire et que les infos de l'entreprise sont fournies...
                if user_type == User.USER_TYPE_BUSINESS and company_info:
                    company_name = company_info.get('name')
                    if not company_name:
                        raise exceptions.ValidationError({'company_info': "Le nom de l'entreprise est requis."})

                    new_company = Company.objects.create(
                        name=company_name,
                        address=company_info.get('address', ''),
                        phone_number=company_info.get('phone_number', ''),
                        description=company_info.get('description', '')
                    )
                    user.company = new_company
                    user.save()

                return user
        except Exception as e:
            # Si une erreur se produit (ex: validation, base de données),
            # on lève une erreur de validation propre au lieu de planter.
            raise serializers.ValidationError(str(e))

# ===================================================================
# == SERIALIZER DE MISE À JOUR (POUR MODIFIER LE PROFIL)
# ===================================================================
class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la MISE À JOUR partielle du profil d'un utilisateur.
    Permet de modifier uniquement les champs autorisés.
    """
    class Meta:
        model = User
        # L'utilisateur peut mettre à jour ces champs. L'avatar est géré ici.
        fields = ['username', 'first_name', 'last_name', 'preferences', 'avatar']
        extra_kwargs = {
            'avatar': {'required': False} # L'avatar n'est pas obligatoire à chaque mise à jour
        }

# ===================================================================
# == SERIALIZER SIMPLE (POUR LES RELATIONS IMBRIQUÉES)
# ===================================================================
class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Serializer ultra-léger pour afficher des infos minimales sur un utilisateur
    dans un autre objet (ex: l'instructeur d'une activité).
    Ce fichier est parfait, aucun changement nécessaire.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'type')
        read_only_fields = fields
