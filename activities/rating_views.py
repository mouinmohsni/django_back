# activities/rating_views.py (NOUVEAU ET CORRIGÉ)

from rest_framework import viewsets, permissions, serializers
from .models import Activity, ActivityRating
from .rating_serializers import ActivityRatingSerializer

class ActivityRatingViewSet(viewsets.ModelViewSet):
    queryset = ActivityRating.objects.all()
    serializer_class = ActivityRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Cette ligne est correcte et nécessaire pour que le routeur imbriqué fonctionne.
    lookup_url_kwarg = 'activity_pk'

    def get_queryset(self):
        # On retourne uniquement les notes pour l'activité spécifiée dans l'URL.
        return self.queryset.filter(activity_id=self.kwargs['activity_pk'])

    def perform_create(self, serializer):
        # On récupère l'activité parente à partir de l'URL.
        activity = Activity.objects.get(pk=self.kwargs['activity_pk'])
        user = self.request.user

        # Validation cruciale : l'utilisateur a-t-il une réservation confirmée ?
        if not activity.bookings.filter(attendee=user, status='confirmed').exists():

            raise serializers.ValidationError("Vous devez avoir participé à cette activité pour la noter.")

        # On injecte l'utilisateur et l'activité avant de sauvegarder.
        serializer.save(user=user, activity=activity)
