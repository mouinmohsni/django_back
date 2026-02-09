# activities/views.py

from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Activity
# ✅ MODIFICATION : On importe les deux serializers spécialisés
from .serializers import ActivityReadSerializer, ActivityWriteSerializer
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


# --- ViewSet pour les Activités (Version Finale et Corrigée) ---
class ActivityViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les opérations CRUD sur les activités.
    Utilise des serializers distincts pour la lecture et l'écriture
    afin de garantir un comportement cohérent.
    """
    queryset = Activity.objects.all().select_related(
        'company',
        'instructor'
    ).prefetch_related(
        'ratings',
        'bookings'
    ).order_by('start_time')

    # ✅ LA CORRECTION DÉFINITIVE : On choisit le bon serializer pour chaque action.
    def get_serializer_class(self):
        """
        Retourne le serializer approprié en fonction de l'action.
        - Lecture ('list', 'retrieve'): ActivityReadSerializer (qui retourne l'URL complète de l'image).
        - Écriture ('create', 'update', 'partial_update'): ActivityWriteSerializer (qui attend un fichier).
        """
        if self.action in ['create', 'update', 'partial_update']:
            return ActivityWriteSerializer
        return ActivityReadSerializer

    def get_queryset(self):
        """
        Filtre dynamiquement les activités à chaque nouvelle requête.
        """
        qs = super().get_queryset()
        if self.action == 'list':
            # Pour la liste publique, on ne montre que les activités futures et publiques.
            return qs.filter(is_public=True, start_time__gt=timezone.now())
        # Pour les autres actions (retrieve, update...), on ne filtre pas ici.
        # Les permissions s'en chargeront.
        return qs

    def get_permissions(self):
        """
        Définit les permissions requises en fonction de l'action demandée.
        """
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, IsBusinessOwner]
        else:  # 'update', 'partial_update', 'destroy'
            self.permission_classes = [permissions.IsAuthenticated, IsActivityCompanyOwner]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Associe automatiquement l'activité à l'entreprise de l'utilisateur connecté
        et sauvegarde l'instructeur si un ID est fourni.
        """
        # On récupère l'ID de l'instructeur depuis les données validées du serializer.
        instructor_id = serializer.validated_data.get('instructor_id')

        # On sauvegarde l'activité en lui passant la compagnie et l'instructeur.
        # Si instructor_id est None, Django l'ignorera, ce qui est parfait.
        serializer.save(
            company=self.request.user.company,
            instructor=instructor_id
        )

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

        # On utilise le serializer de lecture pour être sûr de renvoyer les bonnes données.
        serializer = ActivityReadSerializer(qs, many=True)
        return Response(serializer.data)

