# users/permissions.py

from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBusinessOwner(permissions.BasePermission):
    """
    Permission qui vérifie si l'utilisateur est un propriétaire d'entreprise ('business').
    """
    def has_permission(self, request, view):
        # L'utilisateur doit être connecté ET son type doit être 'business'.
        return request.user.is_authenticated and request.user.type == 'business'

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission qui vérifie si l'utilisateur est le propriétaire de l'objet
    qu'il essaie de modifier, ou s'il est un administrateur.
    """
    def has_object_permission(self, request, view, obj):
        # Un admin ('is_staff') a toujours le droit.
        if request.user.is_staff:
            return True
        # Sinon, l'utilisateur doit être le même que l'objet qu'il regarde/modifie.
        return obj == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Permission personnalisée :
    - Les requêtes en lecture (GET, HEAD, OPTIONS) sont autorisées pour tout le monde.
    - Les requêtes en écriture (POST, PUT, PATCH, DELETE) ne sont autorisées que pour les administrateurs.
    """

    def has_permission(self, request, view):
        # Autorise toutes les requêtes en lecture (GET)
        if request.method in SAFE_METHODS:
            return True

        # Pour les autres méthodes, vérifie si l'utilisateur est un admin
        return request.user and request.user.is_staff