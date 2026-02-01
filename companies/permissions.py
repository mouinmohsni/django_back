# companies/permissions.py
from rest_framework import permissions

class IsCompanyOwner(permissions.BasePermission):
    """
    Permission qui vérifie si l'utilisateur est le propriétaire
    de l'entreprise qu'il essaie de modifier.
    """
    def has_object_permission(self, request, view, obj):
        # L'utilisateur doit être connecté et son champ 'company'
        # doit correspondre à l'objet (l'entreprise) qu'il regarde.
        return request.user.is_authenticated and request.user.company == obj

