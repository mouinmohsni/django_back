# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  UserViewSet,change_password
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # ⚠️ IMPORTANT : Les URLs spécifiques AVANT le routeur !

    # /api/users/token/
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # /api/users/token/refresh/
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', change_password, name='change-password'),

    # Le routeur en DERNIER pour qu'il ne capture pas les URLs ci-dessus
    path('', include(router.urls)),
]
