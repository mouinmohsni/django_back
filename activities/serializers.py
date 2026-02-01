# activities/serializers.py (CORRIGÉ - FINAL)
from rest_framework import serializers
from django.db.models import Avg
from users.models import CustomUser
from .models import Activity
from companies.serializers import SimpleCompanySerializer
from users.serializers import SimpleUserSerializer  # ✅ Import du serializer simple
from .rating_serializers import ActivityRatingReadSerializer


class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer principal pour les activités.
    Utilise des serializers simples pour éviter les importations circulaires.
    """
    company = SimpleCompanySerializer(read_only=True)
    instructor = SimpleUserSerializer(read_only=True)  # ✅ Utilise le serializer simple
    participants_count = serializers.SerializerMethodField()
    effective_location = serializers.SerializerMethodField()
    ratings = ActivityRatingReadSerializer(many=True, read_only=True)
    average_score = serializers.SerializerMethodField()

    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
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

    def get_participants_count(self, obj):
        return obj.bookings.filter(status='confirmed').count()

    def get_effective_location(self, obj: Activity) -> str:
        if obj.location_address:
            return obj.location_address
        if obj.company and hasattr(obj.company, 'address') and obj.company.address:
            return obj.company.address
        return ""

    def get_average_score(self, obj: Activity) -> float | None:
        average = obj.ratings.aggregate(Avg('score')).get('score__avg')
        return round(average, 1) if average is not None else None

    def validate(self, data):
        instructor = data.get('instructor')
        if self.context['request'].method in ['POST', 'PUT']:
            request_user = self.context['request'].user
            if instructor and instructor.company != request_user.company:
                raise serializers.ValidationError({
                    "instructor_id": "L'instructeur sélectionné n'appartient pas à votre entreprise."
                })
        return data


# --- SERIALIZER SIMPLE POUR LES LISTES ---
class SimpleActivitySerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour afficher une activité dans une liste.
    Utilisé pour les endpoints /api/users/{id}/activities/ et /api/companies/{id}/activities/
    """
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


