from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from users.models import CustomUser

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Ceci est notre "traducteur" pour l'inscription. Il sait comment prendre
    des données JSON et les transformer en un nouvel utilisateur dans la base de données.
    """

    # --- Définition des champs supplémentaires ---

    # Par défaut, le champ 'password' du modèle n'est pas fait pour être écrit.
    # On en crée donc un nouveau, virtuel, qui ne sert qu'à l'écriture (write_only=True).
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password], # On applique les validateurs de mot de passe de Django (trop court, etc.)
        style = {'input_type': 'password'}
    )

    # On garde le champ preferences, car le front-end peut l'envoyer.
    # required=False signifie qu'il est optionnel.
    preferences = serializers.JSONField(required=False)

    class Meta:
        model = User
        # On garde la liste des champs du S1. 'id' sera utilisé en lecture seule.
        fields = ('id', 'email', 'username', 'password', 'preferences')

    def create(self, validated_data):
        """
        Cette méthode crée l'utilisateur. Elle est adaptée du S1.
        """
        # On retire le mot de passe des données pour le traiter séparément.
        password = validated_data.pop('password')

        # On retire les préférences. Si elles ne sont pas envoyées, on utilise un dict vide.
        preferences = validated_data.pop('preferences', {})

        # On crée l'utilisateur avec les données restantes.
        # Note : validated_data ne contient plus que 'email' et 'username'.
        user = User.objects.create(
            **validated_data,  # L'astuce **validated_data passe tous les champs restants
            type=User.USER_TYPE_PERSONAL   # On force le type à 'personal'
        )

        # On hache et on définit le mot de passe
        user.set_password(password)

        # On assigne les préférences
        user.preferences = preferences

        # On sauvegarde l'objet utilisateur complet
        user.save()

        return user

# --- CLASSE 2 : Inscription des professionnels ---
class BusinessRegisterSerializer(serializers.ModelSerializer):
    """
    Ce sérialiseur est presque identique au premier, mais avec une différence cruciale :
    il force le type de l'utilisateur à 'business'.
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password], style={'input_type': 'password'}
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
            type=User.USER_TYPE_BUSINESS # La seule différence est ici !
        )
        user.set_password(password)
        user.preferences = preferences
        user.save()
        return user


# --- CLASSE 3 : Affichage des informations utilisateur ---
class UserSerializer(serializers.ModelSerializer):
    """
    Ce sérialiseur est utilisé pour AFFICHER les informations d'un utilisateur
    de manière sécurisée. Il ne sert pas à la création.
    """
    class Meta:
        model = User
        # On définit les champs qu'on veut montrer au monde extérieur.
        fields = ('id', 'email', 'username', 'type', 'preferences', 'avatar', 'is_staff')
        # IMPORTANT : On définit tous ces champs en "lecture seule".
        # Cela empêche quiconque d'utiliser ce sérialiseur pour modifier
        # les informations d'un utilisateur via une requête API.
        read_only_fields = fields

# --- NOUVEAU SÉRIALISEUR POUR LA MISE À JOUR ---
class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Un sérialiseur spécifiquement conçu pour mettre à jour le profil d'un utilisateur.
    Seuls les champs modifiables par l'utilisateur sont inclus.
    """

    class Meta:
        model = CustomUser
        # On liste UNIQUEMENT les champs que l'utilisateur a le droit de modifier.
        fields = ['username', 'preferences', 'avatar']
        # Note : On ne met PAS 'email' ou 'type' ici, car on ne veut pas qu'ils soient modifiables.