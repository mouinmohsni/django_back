# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# --- MODIFICATION : On importe le routeur imbriqué ---
from rest_framework_nested import routers
from .views import UserViewSet, change_password
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# --- 1. Créer le routeur principal pour /users ---
router = routers.SimpleRouter()
router.register(r'', UserViewSet, basename='user')

# --- 2. Créer un routeur imbriqué pour /users/{user_pk}/activities ---
# Le premier argument 'router' est le routeur parent.
# Le deuxième 'r'' est le préfixe de l'URL parente (vide dans notre cas).
# Le troisième 'lookup' est le nom du paramètre dans l'URL.
users_router = routers.NestedSimpleRouter(router, r'', lookup='user')

# On enregistre la sous-route 'activities' sur le UserViewSet.
# Le 'basename' est crucial pour que les noms d'URL soient générés correctement.
users_router.register(r'activities', UserViewSet, basename='user-activities')

# --- 3. Définir les urlpatterns ---
urlpatterns = [
    # URLs spécifiques pour l'authentification (doivent être avant le routeur)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', change_password, name='change-password'),

    # Inclure les URLs du routeur principal (/api/users/ et /api/users/{pk}/)
    path('', include(router.urls)),

    # Inclure les URLs du routeur imbriqué (/api/users/{user_pk}/activities/)
    path('', include(users_router.urls)),
]
