from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from django.db import transaction
from .models import Booking
from .serializers import BookingSerializer, CreateBookingSerializer


class BookingViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
    ViewSet gérant les réservations multi-personnes de manière atomique.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """L'utilisateur ne voit que ses propres réservations."""
        return Booking.objects.filter(attendee=self.request.user).order_by('activity__start_time')

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateBookingSerializer
        return BookingSerializer

    def create(self, request, *args, **kwargs):
        """
        Surcharge pour permettre la mise à jour dynamique du nombre de places.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        activity = serializer.validated_data['activity']
        requested_nb = serializer.validated_data.get('nb_persone', 1)
        user = self.request.user

        with transaction.atomic():
            # Chercher une réservation existante
            booking = Booking.objects.filter(attendee=user, activity=activity).first()

            # Calcul de la différence pour vérifier les places disponibles
            current_nb = booking.nb_persone if booking else 0
            diff = requested_nb - current_nb

            # Vérification de la capacité de l'activité
            # (Note: Assurez-vous que activity.places_disponibles est bien calculé dans votre modèle Activity)
            if diff > 0 and activity.places_disponibles < diff:
                return Response({
                    "error": f"Plus assez de places. Il reste {activity.places_disponibles} places.",
                    "available": activity.places_disponibles
                }, status=status.HTTP_400_BAD_REQUEST)

            # Mise à jour ou Création
            if booking:
                booking.nb_persone = requested_nb
                booking.save()
                return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)
            else:
                new_booking = Booking.objects.create(
                    attendee=user,
                    activity=activity,
                    nb_persone=requested_nb
                )
                return Response(BookingSerializer(new_booking).data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """Suppression complète de la réservation."""
        instance.delete()
