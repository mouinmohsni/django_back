# activities/views.py (CORRIGÉ)

from rest_framework import viewsets, permissions
from .models import Activity
from .serializers import ActivitySerializer
from users.permissions import IsBusinessOwner # Assurez-vous que ce chemin est correct
from django.utils import timezone

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
