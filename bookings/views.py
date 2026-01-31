# bookings/views.py

from rest_framework import viewsets, mixins, permissions
from .models import Booking
from .serializers import BookingSerializer, CreateBookingSerializer

class BookingViewSet(mixins.CreateModelMixin,   # Ajoute .create() -> POST
                     mixins.ListModelMixin,     # Ajoute .list() -> GET (liste)
                     mixins.RetrieveModelMixin, # Ajoute .retrieve() -> GET (détail)
                     mixins.DestroyModelMixin,  # Ajoute .destroy() -> DELETE
                     viewsets.GenericViewSet):
    """
       Ce ViewSet permet de lister, créer, voir le détail et supprimer des réservations.
       La mise à jour (PUT/PATCH) n'est pas autorisée.
       """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Cette méthode garantit que l'utilisateur ne voit que ses propres réservations.
        C'est une mesure de sécurité cruciale.
        """
        return Booking.objects.filter(attendee=self.request.user).order_by('activity__start_time')

    def get_serializer_class(self):
        """
        Choisit le bon sérialiseur en fonction de l'action.
        """
        if self.action == 'create':
            return CreateBookingSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        """
        Lors de la création, lie automatiquement la réservation à l'utilisateur connecté.
        """
        serializer.save(attendee=self.request.user)
