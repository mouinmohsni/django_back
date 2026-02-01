# activities/views.py (CORRIGÉ)
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from .models import Activity
from .serializers import ActivitySerializer
from users.permissions import IsBusinessOwner # Assurez-vous que ce chemin est correct
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

# À l'intérieur de votre ViewSet ou dans get_queryset :
queryset = Activity.objects.filter(is_public=True, start_time__gt=timezone.now()).order_by('start_time')


# --- Permission Personnalisée pour les Activités ---
class IsActivityCompanyOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.company == request.user.company

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.filter(is_public=True, start_time__gt=timezone.now()).order_by('start_time')
    serializer_class = ActivitySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            self.permission_classes = [IsBusinessOwner]
        else:
            self.permission_classes = [IsActivityCompanyOwner]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

    @action(detail=False, methods=['get'], url_path='recommendations', permission_classes=[permissions.AllowAny])
    def recommendations(self, request):
        """
        GET /api/activities/recommendations/?condition=Clear
        On filtre simplement sur venue ('inside' ou 'outside') et on trie par rating.
        """
        condition = request.query_params.get('condition')
        if not condition:
            return Response(
                {'error': 'Le paramètre "condition" est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # si pluie/neige/orage => on propose les venues 'inside', sinon 'outside'
        indoor_conditions = ['Rain', 'Snow', 'Thunderstorm']
        use_outdoor = condition not in indoor_conditions

        qs = self.get_queryset().filter(
            Q(venue='outside') if use_outdoor else Q(venue='inside')
        )

        # tri par rating décroissant, on limite à 12 recommandations
        qs = qs.order_by('-rating')[:12]

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
