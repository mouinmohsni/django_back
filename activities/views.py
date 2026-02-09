# activities/views.py

from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Activity
# ✅ On importe uniquement le serializer principal
from .serializers import ActivitySerializer
from users.permissions import IsBusinessOwner


# --- Permission Personnalisée pour les Activités ---
class IsActivityCompanyOwner(permissions.BasePermission):
    """
    Vérifie que l'utilisateur est authentifié et que l'activité
    appartient bien à l'entreprise de l'utilisateur.
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated and hasattr(request.user, 'company')):
            return False
        return obj.company == request.user.company


# --- ViewSet pour les Activités (Version Nettoyée) ---
class ActivityViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les opérations CRUD sur les activités.
    Utilise un seul serializer intelligent pour toutes les actions.
    """
    # ✅ On définit le serializer par défaut une seule fois.
    serializer_class = ActivitySerializer

    queryset = Activity.objects.all().select_related(
        'company',
        'instructor'
    ).prefetch_related(
        'ratings',
        'bookings'
    ).order_by('start_time')

    # ✅ La méthode 'get_serializer_class' a été supprimée car elle est inutile.

    def get_queryset(self):
        """
        Filtre dynamiquement les activités à chaque nouvelle requête.
        """
        qs = super().get_queryset()
        if self.action == 'list':
            return qs.filter(is_public=True, start_time__gt=timezone.now())
        return qs

    def get_permissions(self):
        """
        Définit les permissions requises en fonction de l'action demandée.
        """
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, IsBusinessOwner]
        else:
            self.permission_classes = [permissions.IsAuthenticated, IsActivityCompanyOwner]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Associe automatiquement l'activité à l'entreprise de l'utilisateur connecté lors de la création.
        """
        serializer.save(company=self.request.user.company)

    @action(detail=False, methods=['get'], url_path='recommendations', permission_classes=[permissions.AllowAny])
    def recommendations(self, request):
        """
        Endpoint pour les recommandations météo.
        """
        condition = request.query_params.get('condition')
        if not condition:
            return Response(
                {'error': 'Le paramètre "condition" est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        indoor_conditions = ['Rain', 'Snow', 'Thunderstorm']
        venue_filter = 'inside' if condition in indoor_conditions else 'outside'
        qs = self.get_queryset().filter(venue=venue_filter)
        qs = qs.order_by('start_time')[:12]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)