# activities/rating_serializers.py
from rest_framework import serializers
from .models import ActivityRating

# activities/rating_serializers.py

class ActivityRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityRating
        # On retire 'activity' et 'user' des champs modifiables
        fields = ['id', 'activity', 'user', 'score', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'activity', 'created_at'] # <-- CORRECTION

    def validate(self, data):
        # La seule validation qui reste ici est de s'assurer que le payload n'est pas vide.
        score = data.get('score')
        comment = data.get('comment', '').strip()  # .strip() pour enlever les espaces vides

        if score is None and not comment:
            raise serializers.ValidationError("Vous devez fournir au moins une note ou un commentaire.")

        return data

class ActivityRatingReadSerializer(serializers.ModelSerializer):
    # On peut même ajouter le nom de l'utilisateur pour un affichage plus riche
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = ActivityRating
        fields = ['id', 'user_name', 'score', 'comment', 'created_at']
