from rest_framework import serializers
from .models import Booking
from activities.serializers import ActivitySerializer


class BookingSerializer(serializers.ModelSerializer):
    """Utilisé pour l'affichage des réservations (Lecture)"""
    activity = ActivitySerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'activity', 'nb_persone', 'status', 'booking_time']


class CreateBookingSerializer(serializers.ModelSerializer):
    """Utilisé pour créer ou mettre à jour une réservation (Écriture)"""

    class Meta:
        model = Booking
        # ✅ Synchronisé : on utilise bien 'nb_persone'
        fields = ['activity', 'nb_persone']

    def validate_nb_persone(self, value):
        """Sécurité supplémentaire : on ne peut pas réserver 0 ou moins"""
        if value < 1:
            raise serializers.ValidationError("Le nombre de personnes doit être au moins de 1.")
        return value
