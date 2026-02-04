# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CoachViewSet, change_password
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'users'

# --- 1. Créer un routeur principal ---
# Ce routeur gérera /users/ et /coaches/ comme des ressources distinctes.
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'coaches', CoachViewSet, basename='coach')

# --- 2. Définir les urlpatterns ---
urlpatterns = [
    # URLs spécifiques pour l'authentification
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', change_password, name='change-password'),

    # Inclure toutes les URLs générées par le routeur.
    # Cela créera automatiquement :
    #   - /api/users/
    #   - /api/users/{pk}/
    #   - /api/users/me/
    #   - /api/users/me/update/
    #   - /api/coaches/
    #   - /api/coaches/{pk}/
    #   - /api/coaches/{pk}/activities/  <-- NOTRE NOUVEL ENDPOINT !
    path('', include(router.urls)),
]
