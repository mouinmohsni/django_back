# users/views.py

from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q

# On importe nos sérialiseurs
from .serializers import RegisterSerializer, BusinessRegisterSerializer, UserSerializer, UserUpdateSerializer
# On importe nos nouvelles permissions personnalisées
from .permissions import IsBusinessOwner, IsOwnerOrAdmin

User = get_user_model()


# --- Vues d'Inscription (inchangées) ---
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class BusinessRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = BusinessRegisterSerializer


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

    from .serializers import  UserUpdateSerializer
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
        if self.action == 'list':
            # Tout utilisateur connecté peut lister (le queryset s'occupera de filtrer ce qu'il voit).
            self.permission_classes = [permissions.IsAuthenticated]
        # Ces actions concernent un objet spécifique (ex: GET /api/users/123/)
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Pour voir/modifier/supprimer un objet, on vérifie que c'est le sien ou qu'on est admin.
            self.permission_classes = [IsOwnerOrAdmin]
        # Actions personnalisées pour la gestion d'équipe
        elif self.action in ['add_coach', 'remove_coach']:
            # Seul un propriétaire d'entreprise peut faire ces actions.
            self.permission_classes = [IsBusinessOwner]
        # Action pour récupérer son propre profil
        elif self.action == 'me':
            self.permission_classes = [permissions.IsAuthenticated]
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

    @action(detail=False, methods=['post'], url_path='add-coach')
    def add_coach(self, request):
        """
        Permet à un propriétaire ('business') de créer un compte 'coach' et de le lier à son entreprise.
        """
        owner = request.user
        if not owner.company:
            return Response({'detail': "Vous devez d'abord créer le profil de votre entreprise."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Le RegisterSerializer crée un utilisateur 'personal' par défaut.
            coach_user = serializer.save()
            # Nous le mettons à jour pour en faire un coach de la bonne entreprise.
            coach_user.type = User.USER_TYPE_COACH
            coach_user.company = owner.company
            coach_user.save()
            # On renvoie les données du coach formatées par le UserSerializer.
            return Response(UserSerializer(coach_user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='remove-coach')
    def remove_coach(self, request, pk=None):
        """
        Permet à un propriétaire de dissocier un coach de son entreprise.
        L'URL sera /api/users/{id_du_coach}/remove-coach/
        """
        owner = request.user
        if not owner.company:
            return Response({'detail': "Vous n'avez pas d'entreprise."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # On s'assure que le coach à dissocier existe et appartient bien à l'entreprise du propriétaire.
            coach_to_remove = User.objects.get(pk=pk, company=owner.company, type=User.USER_TYPE_COACH)
        except User.DoesNotExist:
            return Response({'detail': 'Ce coach est introuvable ou ne fait pas partie de votre entreprise.'}, status=status.HTTP_404_NOT_FOUND)

        # On ne supprime pas le coach, on le détache de l'entreprise.
        coach_to_remove.company = None
        coach_to_remove.save()
        return Response({'status': f"Le coach {coach_to_remove.username} a été dissocié de votre entreprise."}, status=status.HTTP_200_OK)



