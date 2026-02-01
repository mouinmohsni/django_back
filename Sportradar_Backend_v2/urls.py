# Sportradar_Backend_v2/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

from activities.views import ActivityViewSet
from weather.views import weather_api

urlpatterns = [
    path('admin/', admin.site.urls),

    # Routes Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Routes API
    path('api/users/', include('users.urls')),
    path('api/companies/', include('companies.urls')),
    path('api/activities/', include('activities.urls')),
    path('api/bookings/', include('bookings.urls')),

path('api/weather/', weather_api, name='api-weather'),
    # Route explicite pour les recommandations
    path(
        'api/activities/recommendations/',
        ActivityViewSet.as_view({'get': 'recommendations'}),
        name='activity-recommendations'
    ),

]

# Gestion des fichiers médias en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
