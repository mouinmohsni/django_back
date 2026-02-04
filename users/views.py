# users/views.py
from django.contrib.auth.password_validation import validate_password
from rest_framework import viewsets, permissions, status
from rest_framework import serializers # <--- AJOUTEZ CETTE LIGNE
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.db.models import Q

# On importe les serializers renommés et spécialisés
from .serializers import (
    UserCreateSerializer,
    UserReadSerializer,
    UserUpdateSerializer
)
from .permissions import IsOwnerOrAdmin

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les utilisateurs avec une logique de rôles et d'entreprise.
    - La création utilise UserCreateSerializer.
    - La lecture (liste/détail) utilise UserReadSerializer.
    - La mise à jour utilise UserUpdateSerializer.
    """
    queryset = User.objects.all().order_by('username')

    # Définition des permissions par défaut. On les précisera dans get_permissions.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """
        Retourne le sérialiseur approprié en fonction de l'action.
        C'est la méthode la plus propre pour gérer plusieurs serializers.
        """
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        # Pour 'list', 'retrieve', 'me', et toutes les autres actions de lecture,
        # on utilise le serializer sécurisé qui n'expose pas de données sensibles.
        return UserReadSerializer

    def get_permissions(self):
        """
        Définit les permissions requises pour chaque action.
        """
        if self.action == 'create':
            # Tout le monde peut tenter de s'inscrire.
            self.permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Seul le propriétaire du compte ou un admin peut modifier/supprimer.
            self.permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'me':
            # Seul un utilisateur authentifié peut accéder à son propre profil via /me/.
            self.permission_classes = [permissions.IsAuthenticated]

        # Pour les autres actions ('list', 'retrieve'), on garde la permission par défaut
        # de la classe (IsAuthenticatedOrReadOnly).
        return super().get_permissions()

    def get_queryset(self):
        """
        Filtre la liste des utilisateurs.
        - Si l'utilisateur est authentifié, il voit tout le monde.
        - Sinon, il ne voit personne sur cet endpoint.
        """
        user = self.request.user
        qs = super().get_queryset()

        if user.is_authenticated:
            # L'utilisateur est connecté, il peut voir tout le monde.
            return qs

        # Le visiteur non connecté ne voit personne sur /api/users/.
        # Il doit utiliser l'endpoint /api/coaches/.
        return qs.none()

    def perform_destroy(self, instance):
        """ Surcharge pour une "suppression douce" (désactivation). """
        instance.is_active = False
        instance.save()
        # On pourrait aussi anonymiser l'email pour le RGPD, par exemple.
        # instance.email = f"deleted_{instance.id}@example.com"

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Endpoint pratique (/api/users/me/) qui renvoie les données de l'utilisateur connecté.
        Utilise le serializer de lecture (UserReadSerializer).
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], url_path='me/update')
    def update_me(self, request, *args, **kwargs):
        """
        Endpoint pour que l'utilisateur connecté mette à jour son propre profil.
        Utilise le serializer de mise à jour (UserUpdateSerializer).
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)  # partial=True pour PATCH

        # CORRECTION : On instancie DIRECTEMENT le bon serializer.
        # On ignore get_serializer_class() qui se trompait.
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        # On renvoie les données mises à jour avec le serializer de LECTURE pour être cohérent.
        # C'est une bonne pratique de renvoyer les données formatées pour la lecture.
        read_serializer = UserReadSerializer(user)
        return Response(read_serializer.data)


# ===================================================================
# == VUE INDÉPENDANTE POUR LE CHANGEMENT DE MOT DE PASSE
# ===================================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Permet à un utilisateur connecté de changer son mot de passe.
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response({'error': 'Les champs "old_password" et "new_password" sont requis.'}, status=400)

    if not user.check_password(old_password):
        return Response({'old_password': ['Mot de passe actuel incorrect.']}, status=400)

    # Valider le nouveau mot de passe avec les validateurs de Django
    try:
        validate_password(new_password, user)
    except serializers.ValidationError as e:
        return Response({'new_password': e.messages}, status=400)

    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request, user)  # Maintient la session de l'utilisateur active

    return Response({'detail': 'Mot de passe modifié avec succès.'}, status=status.HTTP_200_OK)


# ===================================================================
# == NOUVEAU VIEWSET DÉDIÉ AUX COACHS
# ===================================================================
class CoachViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Un ViewSet public en lecture seule pour lister tous les utilisateurs
    ayant le rôle de 'coach'.
    """
    # Le queryset filtre directement pour ne garder que les coachs.
    queryset = User.objects.filter(type=User.USER_TYPE_COACH).order_by('first_name')

    # On utilise le serializer de lecture pour ne pas exposer de données sensibles.
    serializer_class = UserReadSerializer

    # Tout le monde peut accéder à cette liste.
    permission_classes = [permissions.AllowAny]