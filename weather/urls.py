# weather/urls.py
from django.urls import path
from .views import weather_api

urlpatterns = [
    # GET /api/weather/?lat=<lat>&lon=<lon>
    path('', weather_api, name='api-weather'),
]
