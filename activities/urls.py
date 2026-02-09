# activities/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivityViewSet
from .rating_views import ActivityRatingViewSet

# Routeur simple pour les activités
router = DefaultRouter()
router.register(r'', ActivityViewSet, basename='activity')

# Pour les ratings, on va utiliser une approche manuelle au lieu du NestedRouter

urlpatterns = [
    path('', include(router.urls)),
    # Routes manuelles pour les ratings
    path('<int:activity_pk>/ratings/',
         ActivityRatingViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='activity-rating-list'),
    path('<int:activity_pk>/ratings/<int:pk>/',
         ActivityRatingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='activity-rating-detail'),
]
