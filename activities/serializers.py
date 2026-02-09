# activities/serializers.py

from rest_framework import serializers
from django.db.models import Avg
from users.models import CustomUser
from .models import Activity
from companies.serializers import SimpleCompanySerializer
from users.serializers import SimpleUserSerializer
from .rating_serializers import ActivityRatingReadSerializer

# ===================================================================
# == CHAMP PERSONNALISÉ POUR L'IMAGE (LA SOLUTION HYBRIDE)
# ===================================================================
class HybridImageField(serializers.Field):
    """
    Un champ de serializer personnalisé qui peut accepter :
    1. Un fichier téléversé (pour les formulaires web).
    2. Une chaîne de caractères (le Public ID de Cloudinary, pour les scripts).
    """
    def to_internal_value(self, data):
        # Si la donnée est une chaîne (ex: "media/activity_images/yoga.jpg"),
        # on la retourne telle quelle. Le modèle la sauvegardera.
        if isinstance(data, str):
            return data
        # Si la donnée est un fichier, on le retourne. Le modèle le téléversera.
        # DRF gère automatiquement les fichiers téléversés.
        return data

    def to_representation(self, value):
        # Pour l'affichage, on retourne simplement le chemin de l'image.
        return value.name if hasattr(value, 'name') else str(value)

# ===================================================================
# == SERIALIZER PRINCIPAL ET UNIQUE
# ===================================================================
class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer principal et UNIQUE pour les activités.
    Gère la création, la lecture et la mise à jour de manière flexible.
    """
    # ✅ On utilise notre nouveau champ personnalisé.
    image = HybridImageField(required=False, allow_null=True)

    company = SimpleCompanySerializer(read_only=True)
    instructor = SimpleUserSerializer(read_only=True)
    participants_count = serializers.SerializerMethodField(read_only=True)
    effective_location = serializers.SerializerMethodField(read_only=True)
    ratings = ActivityRatingReadSerializer(many=True, read_only=True)
    average_score = serializers.SerializerMethodField(read_only=True)

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
            'instructor_id', 'sport_zen'
        ]
        read_only_fields = [
            'id', 'company', 'instructor', 'created_at',
            'participants_count', 'effective_location',
            'ratings', 'average_score'
        ]

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


# --- SimpleActivitySerializer (pour les listes légères, ne change pas) ---
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

