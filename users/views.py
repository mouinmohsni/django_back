# users/views.py

from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.db.models import Q

# On importe nos sérialiseurs
from .serializers import (


    UserSerializer,
    UserUpdateSerializer
)
# On importe nos nouvelles permissions personnalisées
from .permissions import IsBusinessOwner, IsOwnerOrAdmin

User = get_user_model()


# --- Vues d'Inscription (inchangées) ---






# --- Le UserViewSet, version professionnelle ---
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les utilisateurs avec une logique de rôles et d'entreprise.
    - Un admin voit tout.
    - Un 'business' user voit son équipe (les coachs actifs de son entreprise).
    - Un 'coach' ou 'personal' user ne voit que son propre profil.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Cette méthode est le cœur de notre logique de visibilité.
        Elle filtre la liste des utilisateurs que chaque rôle a le droit de voir.
        """
        user = self.request.user

        # 1. Cas du visiteur non connecté
        if not user.is_authenticated:
            return User.objects.filter(type=User.USER_TYPE_COACH)

        # 2. Cas de l'administrateur (voit tout)
        if user.is_staff:
            return User.objects.all()

        # 3. Cas du propriétaire d'entreprise
        if user.type == User.USER_TYPE_BUSINESS and user.company:
            # Il voit son propre profil ET les coachs ACTIFS de son entreprise.
            return User.objects.filter(
                Q(pk=user.pk) |
                Q(company=user.company, is_active=True, type=User.USER_TYPE_COACH)
            )

        # 4. NOUVEAU CAS : Le coach
        if user.type == User.USER_TYPE_COACH:
            # Il voit son propre profil ET les participants confirmés à SES activités.

            # On récupère les IDs de tous les participants (attendees) des activités
            # où l'utilisateur actuel est l'instructeur.
            participant_ids = User.objects.filter(
                bookings_as_attendee__activity__instructor=user,
                bookings_as_attendee__status='confirmed'
            ).values_list('id', flat=True)

            # Le coach voit :
            # - Lui-même
            # - Tous les autres coachs (pour la collaboration)
            # - Les participants à ses cours
            return User.objects.filter(
                Q(pk=user.pk) |  # Soit c'est lui-même
                Q(type=User.USER_TYPE_COACH) |  # Soit c'est un autre coach
                Q(id__in=list(set(participant_ids)))  # Soit c'est un participant de ses cours
            ).distinct()

        # 5. NOUVEAU CAS : Le client ('personal')
        if user.type == User.USER_TYPE_PERSONAL:
            # Il voit son propre profil ET tous les coachs.
            return User.objects.filter(
                Q(pk=user.pk) | Q(type=User.USER_TYPE_COACH)
            )

        # 6. Cas par défaut (au cas où, ne devrait jamais être atteint si les types sont bien gérés)
        return User.objects.filter(pk=user.pk)

    def get_serializer_class(self):
        """
        Retourne le sérialiseur approprié en fonction de l'action demandée.
        """
        # Si l'action est une mise à jour (PUT ou PATCH)
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer

        # Pour toutes les autres actions (list, retrieve, create...), on utilise le sérialiseur par défaut.
        return UserSerializer

    def get_permissions(self):
        """
        Définit les permissions requises pour chaque type d'action (créer, lister, etc.).
        """
        # L'action 'list' est pour voir la liste (GET /api/users/)
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action == 'list':
            # ✅ MODIFIÉ : Tout le monde peut lister les coaches (même non connecté)
            self.permission_classes = [permissions.AllowAny]
        # Voir le détail d'un utilisateur
        elif self.action == 'retrieve':
            # ✅ MODIFIÉ : Tout le monde peut voir le profil d'un coach
            self.permission_classes = [permissions.AllowAny]
        # Modifier/supprimer un utilisateur
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Seul le propriétaire ou un admin peut modifier
            self.permission_classes = [IsOwnerOrAdmin]
        # Actions personnalisées pour la gestion d'équipe
        elif self.action in ['add_coach', 'remove_coach']:
            # Seul un propriétaire d'entreprise peut faire ces actions.
            self.permission_classes = [IsBusinessOwner]
        # Action pour récupérer son propre profil
        elif self.action == 'me':
            self.permission_classes = [permissions.IsAuthenticated]
        # NOUVEAU : Action pour récupérer les activités d'un coach
        elif self.action == 'activities':
            # Tout le monde peut voir les activités d'un coach (lecture publique)
            self.permission_classes = [permissions.AllowAny]
        # ✅ NOUVEAU : Actions pour les coaches (quitter/rejoindre une entreprise)

        else:
            # Par sécurité, si une action n'est pas listée, on la réserve aux admins.
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    def perform_destroy(self, instance):
        """ Surcharge de la suppression pour faire une "suppression douce". """
        instance.is_active = False
        instance.save()

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """ Une URL pratique (/api/users/me/) qui renvoie toujours les données de l'utilisateur connecté. """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


    # ============================================
    # 🆕 NOUVELLE ACTION : Récupérer les activités d'un coach
    # ============================================
    @action(detail=True, methods=['get'], url_path='activities')
    def activities(self, request, pk=None):
        """
        Endpoint pour récupérer toutes les activités d'un coach.
        URL : GET /api/users/{user_id}/activities/

        Retourne la liste des activités où cet utilisateur est l'instructeur.
        """
        user = self.get_object()

        # Vérifier que l'utilisateur est un coach
        if user.type != User.USER_TYPE_COACH:
            return Response(
                {"detail": "Cet utilisateur n'est pas un coach."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupérer les activités où cet utilisateur est l'instructeur
        activities = user.instructed_activities.all()

        # Import local pour éviter l'importation circulaire
        from activities.serializers import ActivitySerializer
        serializer = ActivitySerializer(activities, many=True)
        print("===========================",serializer.data)

        return Response(serializer.data)



# ============================================
# 🆕 FONCTION INDÉPENDANTE : Changement de mot de passe
# ============================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Permet à un utilisateur connecté de changer son mot de passe.
    URL : POST /auth/change-password/

    Body : {
        "old_password": "ancien_mot_de_passe",
        "new_password": "nouveau_mot_de_passe"
    }
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not user.check_password(old_password):
        return Response({'old_password': ['Mot de passe incorrect']}, status=400)

    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request, user)  # Garde la session active

    return Response({'detail': 'Mot de passe modifié avec succès'})
