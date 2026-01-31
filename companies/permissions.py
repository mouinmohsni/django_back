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



class IsCompanyOwner(permissions.BasePermission):
    """
    Permission au niveau de l'objet.
    Vérifie si l'utilisateur qui fait la requête est bien le propriétaire
    de l'entreprise (l'objet 'obj').
    """
    def has_object_permission(self, request, view, obj):
        # L'utilisateur doit être authentifié.
        if not request.user.is_authenticated:
            return False
        # Le champ 'company' de l'utilisateur doit être le même que l'entreprise
        # qu'il essaie de modifier/supprimer.
        # 'obj' ici est une instance du modèle Company.
        return request.user.is_authenticated and request.user.company == obj

