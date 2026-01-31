# users/urls.py (CORRIGÉ)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, BusinessRegisterView, UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
# CORRECTION : Le préfixe est vide (r'') car '/api/users/' est déjà dans le fichier principal.
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # Les URLs du routeur sont maintenant / (liste) et /{pk}/ (détail)
    path('', include(router.urls)),

    # Les URLs manuelles sont relatives à /api/users/
    # /api/users/register/
    path('register/', RegisterView.as_view(), name='register'),
    # /api/users/register-business/
    path('register-business/', BusinessRegisterView.as_view(), name='register-business'),
    # /api/users/token/
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # /api/users/token/refresh/
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
