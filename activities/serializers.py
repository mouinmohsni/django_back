# activities/serializers.py
#muin
from rest_framework import serializers
from django.db.models import Avg
from users.models import CustomUser
from .models import Activity
from companies.serializers import SimpleCompanySerializer
from users.serializers import SimpleUserSerializer
from .rating_serializers import ActivityRatingReadSerializer

# Le HybridImageField a été COMPLÈTEMENT SUPPRIMÉ.

# ===================================================================
# == SERIALIZER PRINCIPAL ET UNIQUE (VERSION STANDARD)
# ===================================================================
class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer principal et UNIQUE pour les activités.
    Il se comporte comme un serializer Django standard.
    Le champ 'image' attend un fichier et retourne une URL complète.
    """
    company = SimpleCompanySerializer(read_only=True)
    instructor = SimpleUserSerializer(read_only=True)
    effective_location = serializers.SerializerMethodField(read_only=True)
    ratings = ActivityRatingReadSerializer(many=True, read_only=True)
    average_score = serializers.SerializerMethodField(read_only=True)
    participants_count = serializers.ReadOnlyField()
    places_disponibles = serializers.ReadOnlyField()


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
            'participants_count','places_disponibles', 'effective_location', 'ratings', 'average_score',
            'instructor_id', 'sport_zen'
        ]
        # On s'assure que les champs en lecture seule sont corrects.
        read_only_fields = [
            'id', 'company', 'instructor', 'created_at',
            'participants_count','places_disponibles', 'effective_location',
            'ratings', 'average_score'
        ]



    def get_effective_location(self, obj: Activity) -> str:
        if obj.location_address:
            return obj.location_address
        if obj.company and obj.company.address:
            return obj.company.address
        return ""

    def get_average_score(self, obj: Activity) -> float | None:
        average = obj.ratings.aggregate(Avg('score')).get('score__avg')
        return round(average, 1) if average is not None else None


# --- SimpleActivitySerializer (ne change pas, il est déjà simple) ---
class SimpleActivitySerializer(serializers.ModelSerializer):
    # ... (le contenu de cette classe ne change pas)
    company = SimpleCompanySerializer(read_only=True)
    instructor = SimpleUserSerializer(read_only=True)
    average_score = serializers.SerializerMethodField()
    participants_count = serializers.ReadOnlyField()
    places_disponibles = serializers.ReadOnlyField()

    class Meta:
        model = Activity
        fields = [
            'id', 'name', 'description', 'category', 'image',
            'company', 'instructor', 'start_time', 'duration',
            'price', 'level', 'average_score','participants_count', 'max_participants','places_disponibles'
        ]
        read_only_fields = fields

    def get_average_score(self, obj: Activity) -> float | None:
        average = obj.ratings.aggregate(Avg('score')).get('score__avg')
        return round(average, 1) if average is not None else None

    def get_participants_count(self, obj):
        return obj.bookings.filter(status='confirmed').count()