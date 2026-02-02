# activities/views.py

from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Activity
from .serializers import ActivitySerializer
from users.permissions import IsBusinessOwner  # Assurez-vous que ce chemin est correct


# --- Permission Personnalisée pour les Activités ---
class IsActivityCompanyOwner(permissions.BasePermission):
    """
    Vérifie que l'utilisateur est authentifié et que l'activité
    appartient bien à l'entreprise de l'utilisateur.
    """

    def has_object_permission(self, request, view, obj):
        # S'assure que l'utilisateur est connecté et a une entreprise associée
        if not (request.user and request.user.is_authenticated and hasattr(request.user, 'company')):
            return False
        # Vérifie que l'entreprise de l'activité est la même que celle de l'utilisateur
        return obj.company == request.user.company


# --- ViewSet pour les Activités ---
class ActivityViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les opérations CRUD sur les activités.
    """
    # 1. Le queryset de base inclut TOUTES les activités.
    #    Ceci est crucial pour que les opérations comme 'create', 'update', 'delete'
    #    puissent fonctionner correctement en se basant sur l'ID (pk).
    serializer_class = ActivitySerializer

    queryset = Activity.objects.all().select_related(
        'company',
        'instructor'
    ).prefetch_related(
        'ratings',
        'bookings'
    ).order_by('start_time')


    def get_queryset(self):
        """
        Cette méthode est appelée pour les requêtes de type 'list' (GET /api/activities/).
        Elle filtre dynamiquement les activités à chaque nouvelle requête.
        """
        # On part du queryset de base défini pour la classe
        qs = super().get_queryset()

        # Pour les utilisateurs non authentifiés (ou n'importe qui listant les activités),
        # on ne montre que les activités publiques et futures.
        # timezone.now() est maintenant évalué à chaque requête, ce qui est correct.
        if self.action == 'list':
            return qs.filter(is_public=True, start_time__gt=timezone.now())

        # Pour les autres actions (retrieve, update, etc.), on ne filtre pas ici,
        # car les permissions s'en chargeront.
        return qs

    def get_permissions(self):
        """
        Définit les permissions requises en fonction de l'action demandée.
        """
        if self.action in ['list', 'retrieve']:
            # Tout le monde peut voir la liste (filtrée par get_queryset) et le détail.
            self.permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            # Seul un propriétaire d'entreprise peut créer une activité.
            self.permission_classes = [permissions.IsAuthenticated, IsBusinessOwner]
        else:  # 'update', 'partial_update', 'destroy'
            # Seul le propriétaire de l'entreprise à laquelle l'activité appartient peut la modifier/supprimer.
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
        GET /api/activities/recommendations/?condition=Clear
        """
        condition = request.query_params.get('condition')
        if not condition:
            return Response(
                {'error': 'Le paramètre "condition" est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Si pluie/neige/orage => on propose les activités 'indoor', sinon 'outdoor'
        indoor_conditions = ['Rain', 'Snow', 'Thunderstorm']
        venue_filter = 'inside' if condition in indoor_conditions else 'outside'

        # On utilise le queryset de base (toutes les activités) et on applique nos filtres
        qs = self.get_queryset().filter(venue=venue_filter)

        # Tri par rating décroissant (si le champ rating existe sur le modèle)
        # et on limite à 12 recommandations.
        # Note: Le modèle Activity n'a pas de champ 'rating' direct, il faut utiliser l'agrégation.
        # Pour simplifier ici, on trie par date. Pour un tri par note, il faudrait une annotation.
        qs = qs.order_by('start_time')[:12]

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

