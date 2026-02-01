# companies/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer

# On importe la permission de l'application 'users' pour la création
from users.permissions import IsBusinessOwner
# On importe notre nouvelle permission locale pour la modification/suppression
from .permissions import IsCompanyOwner


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour le modèle Company avec des permissions granulaires.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_permissions(self):
        """
        Applique la bonne permission en fonction de l'action demandée.
        """
        # Action de création
        if self.action == 'create':
            # Seul un utilisateur de type 'business' peut créer une entreprise.
            self.permission_classes = [IsBusinessOwner]

        # Actions sur un objet existant (modifier, supprimer)
        elif self.action in ['update', 'partial_update', 'destroy']:
            # L'utilisateur doit être le propriétaire de l'entreprise.
            # IsCompanyOwner sera appelé par DRF.
            self.permission_classes = [IsCompanyOwner]

        # Actions de lecture (lister tout, voir un détail)
        # 'list' correspond à GET /api/companies/
        # 'retrieve' correspond à GET /api/companies/{id}/
        elif self.action in ['list', 'retrieve']:
            # On autorise tout le monde, même les visiteurs non connectés.
            self.permission_classes = [permissions.AllowAny]

        # NOUVEAU : Actions pour récupérer les coaches et activités d'une entreprise
        elif self.action in ['coaches', 'activities']:
            # Tout le monde peut voir les coaches et activités (lecture publique)
            self.permission_classes = [permissions.AllowAny]

        # Par sécurité, si une action inconnue est appelée, on la bloque.
        else:
            self.permission_classes = [permissions.IsAdminUser]

        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Surcharge pour lier automatiquement l'entreprise à l'utilisateur 'business'
        qui vient de la créer.
        """
        company = serializer.save()
        # On met à jour le profil de l'utilisateur qui a fait la requête.
        self.request.user.company = company
        self.request.user.save()

    # ============================================
    # 🆕 NOUVELLE ACTION : Récupérer les coaches d'une entreprise
    # ============================================
    @action(detail=True, methods=['get'], url_path='coaches')
    def coaches(self, request, pk=None):
        """
        Endpoint pour récupérer tous les coaches d'une entreprise.
        URL : GET /api/companies/{company_id}/coaches/

        Retourne la liste des utilisateurs de type 'coach' liés à cette entreprise.
        """
        company = self.get_object()

        # Récupérer tous les coaches de cette entreprise
        # members est le related_name défini dans le modèle User
        from django.contrib.auth import get_user_model
        User = get_user_model()
        coaches = company.members.filter(type=User.USER_TYPE_COACH, is_active=True)  # ✅ CORRIGÉ

        # Import local pour éviter l'importation circulaire
        from users.serializers import SimpleUserSerializer
        serializer = SimpleUserSerializer(coaches, many=True)

        return Response(serializer.data)

    # ============================================
    # 🆕 NOUVELLE ACTION : Récupérer les activités d'une entreprise
    # ============================================
    @action(detail=True, methods=['get'], url_path='activities')
    def activities(self, request, pk=None):
        """
        Endpoint pour récupérer toutes les activités d'une entreprise.
        URL : GET /api/companies/{company_id}/activities/

        Retourne la liste des activités liées à cette entreprise.
        """
        company = self.get_object()

        # Récupérer toutes les activités de cette entreprise
        # activities est la relation inverse de company dans le modèle Activity
        activities = company.activities.all()

        # Import local pour éviter l'importation circulaire
        from activities.serializers import ActivitySerializer
        serializer = ActivitySerializer(activities, many=True, context={'request': request})

        return Response(serializer.data)
