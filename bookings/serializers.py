# bookings/serializers.py

from rest_framework import serializers

from activities.models import Activity
from .models import Booking
# --- CORRECTION ---
# On importe le serializer SIMPLE pour éviter la dépendance circulaire.
from activities.serializers import SimpleActivitySerializer
from users.serializers import UserReadSerializer

class BookingSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la LECTURE des réservations.
    Affiche les détails de l'activité et du participant.
    """
    # On utilise le serializer simple qui n'a pas de dépendances complexes.
    activity = SimpleActivitySerializer(read_only=True)
    attendee = UserReadSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'activity', 'attendee', 'status', 'booking_time']


class CreateBookingSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la CRÉATION d'une réservation.
    L'utilisateur ne doit fournir que l'ID de l'activité.
    """
    activity = serializers.PrimaryKeyRelatedField(
        # On s'assure que l'utilisateur ne peut réserver que des activités publiques et futures.
        queryset=Activity.objects.filter(is_public=True, start_time__gt=serializers.timezone.now())
    )

    class Meta:
        model = Booking
        fields = ['activity']

    def validate(self, data):
        """
        Vérifications métier avant de créer la réservation.
        """
        activity = data['activity']
        attendee = self.context['request'].user

        # 1. Vérifier si l'activité est complète
        confirmed_bookings = activity.bookings.filter(status='confirmed').count()
        if confirmed_bookings >= activity.max_participants:
            raise serializers.ValidationError("Cette activité est complète.")

        # 2. Vérifier si l'utilisateur est déjà inscrit
        if Booking.objects.filter(activity=activity, attendee=attendee).exists():
            raise serializers.ValidationError("Vous êtes déjà inscrit à cette activité.")

        # 3. Vérifier que l'utilisateur est un 'personal' user
        if attendee.type != 'personal':
            raise serializers.ValidationError("Seuls les utilisateurs 'personal' peuvent réserver des activités.")

        return data
