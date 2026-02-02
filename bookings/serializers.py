# bookings/serializers.py

from rest_framework import serializers

from activities.models import Activity
from .models import Booking
from activities.serializers import ActivitySerializer # Pour afficher les détails de l'activité
from users.serializers import  UserReadSerializer  # Pour afficher les détails du participant

class BookingSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la LECTURE des réservations.
    Affiche les détails de l'activité et du participant.
    """
    activity = ActivitySerializer(read_only=True)
    attendee = UserReadSerializer (read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'activity', 'attendee', 'status', 'booking_time']


class CreateBookingSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la CRÉATION d'une réservation.
    L'utilisateur ne doit fournir que l'ID de l'activité.
    """
    # On s'attend à recevoir l'ID de l'activité que l'utilisateur veut réserver.
    activity = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.filter(is_public=True))

    class Meta:
        model = Booking
        fields = ['activity'] # Seul le champ 'activity' est attendu de l'utilisateur.

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
        if not attendee.type == 'personal':
            raise serializers.ValidationError("Seuls les utilisateurs 'personal' peuvent réserver des activités.")

        return data
