# Sportradar_Backend_v2/urls.py (CORRIGÉ)

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

# Sportradar_Backend_v2/urls.py (Alternative PLUS PROPRE)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/companies/', include('companies.urls')),
    path('api/activities/', include('activities.urls')),
    path('api/bookings/', include('bookings.urls')),
    # ...
]


# Gestion des fichiers médias en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
