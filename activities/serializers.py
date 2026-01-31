# activities/serializers.py (CORRIGÉ)

from rest_framework import serializers
from django.db.models import Avg
from users.models import CustomUser
from .models import Activity
from companies.serializers import SimpleCompanySerializer
from users.serializers import UserSerializer
from .rating_serializers import ActivityRatingReadSerializer


class ActivitySerializer(serializers.ModelSerializer):
    company = SimpleCompanySerializer(read_only=True)
    instructor = UserSerializer(read_only=True)
    participants_count = serializers.SerializerMethodField()
    effective_location = serializers.SerializerMethodField()
    ratings = ActivityRatingReadSerializer(many=True, read_only=True)

    # Le nom du champ est 'average_score', mais la méthode s'appelle 'get_average_score'
    average_score = serializers.SerializerMethodField()

    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='instructor', write_only=True,
        required=False, allow_null=True
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

    # --- CORRECTION DE LA MÉTHODE POUR LA MOYENNE ---
    def get_average_score(self, obj: Activity) -> float | None:
        # On calcule la moyenne directement ici.
        average = obj.ratings.aggregate(Avg('score')).get('score__avg')
        return round(average, 1) if average is not None else None

    def validate(self, data):
        instructor = data.get('instructor')
        if self.context['request'].method == 'POST' or self.context['request'].method == 'PUT':
            request_user = self.context['request'].user
            if instructor and instructor.company != request_user.company:
                raise serializers.ValidationError({
                    "instructor_id": "L'instructeur sélectionné n'appartient pas à votre entreprise."
                })
        return data
