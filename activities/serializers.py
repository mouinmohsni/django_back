# activities/serializers.py

from rest_framework import serializers
from django.db.models import Avg
from users.models import CustomUser
from .models import Activity
from companies.serializers import SimpleCompanySerializer
from users.serializers import SimpleUserSerializer
from .rating_serializers import ActivityRatingReadSerializer


class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer principal pour les activités.
    La validation de l'instructeur a été retirée pour plus de flexibilité.
    """
    company = SimpleCompanySerializer(read_only=True)
    instructor = SimpleUserSerializer(read_only=True)
    participants_count = serializers.SerializerMethodField()
    effective_location = serializers.SerializerMethodField()
    ratings = ActivityRatingReadSerializer(many=True, read_only=True)
    average_score = serializers.SerializerMethodField()

    # Ce champ permet de passer un ID d'instructeur lors de la création/mise à jour.
    # Il n'est pas obligatoire (required=False, allow_null=True).
    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(type=CustomUser.USER_TYPE_COACH),
        source='instructor',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Activity
        fields = [
            'id', 'name', 'description', 'category', 'image', 'location_address',
            'company', 'instructor', 'start_time', 'duration', 'max_participants',
            'price', 'level', 'venue', 'is_public', 'created_at',
            'participants_count', 'effective_location', 'ratings', 'average_score',
            'instructor_id'
        ]
        read_only_fields = [
            'company', 'instructor', 'participants_count', 'effective_location',
            'ratings', 'average_score'
        ]

    # ===================================================================
    # == LA MÉTHODE VALIDATE A ÉTÉ COMPLÈTEMENT SUPPRIMÉE
    # ===================================================================
    # (Pas de méthode validate ici)

    def get_participants_count(self, obj):
        return obj.bookings.filter(status='confirmed').count()

    def get_effective_location(self, obj: Activity) -> str:
        if obj.location_address:
            return obj.location_address
        if obj.company and obj.company.address:
            return obj.company.address
        return ""

    def get_average_score(self, obj: Activity) -> float | None:
        average = obj.ratings.aggregate(Avg('score')).get('score__avg')
        return round(average, 1) if average is not None else None


# Le reste du fichier (SimpleActivitySerializer) reste inchangé.
class SimpleActivitySerializer(serializers.ModelSerializer):
    company = SimpleCompanySerializer(read_only=True)
    instructor = SimpleUserSerializer(read_only=True)
    average_score = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            'id', 'name', 'description', 'category', 'image',
            'company', 'instructor', 'start_time', 'duration',
            'price', 'level', 'average_score','participants_count', 'max_participants',
        ]
        read_only_fields = fields


    def get_average_score(self, obj: Activity) -> float | None:
        average = obj.ratings.aggregate(Avg('score')).get('score__avg')
        return round(average, 1) if average is not None else None

    def get_participants_count(self, obj):
        return obj.bookings.filter(status='confirmed').count()


# ... (votre classe ActivitySerializer existante reste ici, inchangée) ...

# ===================================================================
# == NOUVEAU SERIALIZER DE MISE À JOUR (LA CORRECTION)
# ===================================================================
class ActivityUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer spécifique pour la MISE À JOUR d'une activité.
    Il traite le champ 'image' comme une simple chaîne de caractères (CharField)
    pour qu'on puisse lui passer le Public ID de Cloudinary depuis un script.
    """
    # CORRECTION CLÉ : On redéfinit le champ 'image' pour qu'il accepte du texte.
    # 'required=False' et 'allow_blank=True' permettent de ne pas envoyer l'image
    # à chaque mise à jour si on ne veut pas la changer.
    image = serializers.CharField(required=False, allow_blank=True)

    # On s'assure que l'instructor_id est bien géré comme dans l'autre serializer.
    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(type=CustomUser.USER_TYPE_COACH),
        source='instructor',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Activity
        # On liste uniquement les champs qu'on veut pouvoir mettre à jour via notre script.
        fields = [
            'name', 'description', 'category', 'image', 'location_address',
            'start_time', 'duration', 'max_participants', 'price', 'level',
            'venue', 'is_public', 'instructor_id'
        ]

# ... (votre classe SimpleActivitySerializer reste ici, inchangée) ...
