# activities/serializers.py

from rest_framework import serializers
from django.db.models import Avg
from users.models import CustomUser
from .models import Activity
from companies.serializers import SimpleCompanySerializer
from users.serializers import SimpleUserSerializer
from .rating_serializers import ActivityRatingReadSerializer

# ===================================================================
# == SERIALIZER DE LECTURE (CELUI QUI VA RÉSOUDRE LE PROBLÈME)
# ===================================================================
class ActivityReadSerializer(serializers.ModelSerializer):
    """
    Serializer pour AFFICHER les informations d'une activité.
    Le champ 'image' est en lecture seule et retournera l'URL complète.
    """
    company = SimpleCompanySerializer(read_only=True)
    instructor = SimpleUserSerializer(read_only=True)
    participants_count = serializers.SerializerMethodField()
    effective_location = serializers.SerializerMethodField()
    ratings = ActivityRatingReadSerializer(many=True, read_only=True)
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            'id', 'name', 'description', 'category', 'image', 'location_address',
            'company', 'instructor', 'start_time', 'duration', 'max_participants',
            'price', 'level', 'venue', 'is_public', 'created_at',
            'participants_count', 'effective_location', 'ratings', 'average_score',
            'sport_zen'
        ]
        read_only_fields = fields  # Tous les champs sont en lecture seule

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

# ===================================================================
# == SERIALIZER D'ÉCRITURE (POUR CRÉER/MODIFIER)
# ===================================================================
class ActivityWriteSerializer(serializers.ModelSerializer):
    """
    Serializer pour CRÉER ou MODIFIER une activité.
    Le champ 'image' attend un fichier.
    """
    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(type=CustomUser.USER_TYPE_COACH),
        source='instructor',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Activity
        # On liste tous les champs modifiables
        fields = [
            'name', 'description', 'category', 'image', 'location_address',
            'start_time', 'duration', 'max_participants', 'price', 'level',
            'venue', 'is_public', 'instructor_id', 'sport_zen'
        ]
        # On s'assure que le champ image n'est pas obligatoire pour les mises à jour
        extra_kwargs = {
            'image': {'required': False}
        }

# --- SimpleActivitySerializer (ne change pas) ---
class SimpleActivitySerializer(ActivityReadSerializer):
    """
    Version légère du serializer de lecture pour les listes.
    Hérite de ActivityReadSerializer pour garantir la cohérence.
    """
    class Meta(ActivityReadSerializer.Meta):
        # On choisit les champs qu'on veut pour la version simple
        fields = [
            'id', 'name', 'description', 'category', 'image',
            'company', 'instructor', 'start_time', 'duration',
            'price', 'level', 'average_score','participants_count', 'max_participants',
        ]

