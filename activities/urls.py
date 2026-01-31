# activities/urls.py (CORRIGÉ)

from django.urls import path, include
from rest_framework_nested import routers
from .views import ActivityViewSet
from .rating_views import ActivityRatingViewSet # On importe depuis le bon fichier

# 1. On crée un routeur principal simple.
router = routers.SimpleRouter()
# 2. On enregistre la route de base pour les activités. Le préfixe est vide ('')
#    car le préfixe '/api/activities/' est déjà dans le fichier d'URL principal du projet.
router.register(r'', ActivityViewSet, basename='activities')

# 3. On crée le routeur imbriqué.
#    - Il se base sur le 'router' principal.
#    - Le préfixe est vide (r'').
#    - Le 'lookup' est 'activity', qui correspondra à la variable 'activity_pk'.
activities_router = routers.NestedSimpleRouter(router, r'', lookup='activity')
activities_router.register(r'ratings', ActivityRatingViewSet, basename='activity-ratings')

# 4. On combine les URLs générées.
urlpatterns = [
    path('', include(router.urls)),
    path('', include(activities_router.urls)),
]
