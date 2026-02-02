# weather/views.py

import requests
import logging  # Import du module de logging pour un meilleur débogage
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny]) # C'est une bonne pratique de toujours définir les permissions explicitement
def weather_api(request):
    """
    Endpoint pour récupérer les données météo actuelles depuis OpenWeatherMap.
    Accepte les paramètres 'lat' (latitude) et 'lon' (longitude).
    Exemple: /api/weather/?lat=48.85&lon=2.35
    """
    # --- 1. Vérification de la configuration de la clé d'API ---
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key:
        # On log l'erreur côté serveur pour que les développeurs soient au courant.
        # L'utilisateur final n'a pas besoin de connaître la cause exacte.
        logger.error("La clé d'API OPENWEATHER_API_KEY n'est pas configurée dans les variables d'environnement.")
        return Response(
            {'error': "Le service météo est temporairement indisponible en raison d'un problème de configuration."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # --- 2. Validation des paramètres d'entrée ---
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')
    if not lat or not lon:
        return Response(
            {'error': 'Les paramètres "lat" et "lon" sont requis.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # --- 3. Appel à l'API externe ---
    url = (
        'https://api.openweathermap.org/data/2.5/weather'
        f'?lat={lat}&lon={lon}'
        '&units=metric'
        f'&appid={api_key}'
     )

    try:
        resp = requests.get(url, timeout=5) # Le timeout est une bonne pratique
        resp.raise_for_status()  # Lève une exception pour les erreurs HTTP (4xx ou 5xx)
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'appel à OpenWeatherMap: {e}")
        return Response(
            {'error': 'Le service météo externe est actuellement indisponible.'},
            status=status.HTTP_502_BAD_GATEWAY
        )

    # --- 4. Traitement sécurisé de la réponse JSON ---
    data = resp.json()

    # On utilise .get() pour éviter les erreurs si les clés sont manquantes
    main_data = data.get('main', {})
    weather_list = data.get('weather', [])

    if not weather_list:
        logger.warning("La réponse d'OpenWeatherMap ne contient pas de section 'weather'.")
        return Response(
            {'error': 'Les données reçues du service météo sont invalides.'},
            status=status.HTTP_502_BAD_GATEWAY
        )

    weather_data = weather_list[0]

    # Construction de la réponse finale
    response_data = {
        'temp': main_data.get('temp'),
        'condition': weather_data.get('main'),
        'icon': weather_data.get('icon')
    }

    # On vérifie qu'on a bien les données essentielles avant de les renvoyer
    if response_data['temp'] is None or response_data['condition'] is None:
        logger.warning(f"Données météo incomplètes reçues: {data}")
        return Response(
            {'error': 'Les données reçues du service météo sont incomplètes.'},
            status=status.HTTP_502_BAD_GATEWAY
        )

    return Response(response_data, status=status.HTTP_200_OK)

