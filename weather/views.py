import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def weather_api(request):
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')
    if not lat or not lon:
        return Response({'error': 'lat & lon requis'}, status=400)

    url = (
        'https://api.openweathermap.org/data/2.5/weather'
        f'?lat={lat}&lon={lon}'
        '&units=metric'
        f'&appid={settings.OPENWEATHER_API_KEY}'
    )
    resp = requests.get(url, timeout=5)
    if resp.status_code != 200:
        return Response({'error': 'OpenWeather indisponible'}, status=502)

    data = resp.json()
    return Response({
        'temp': data['main']['temp'],
        'condition': data['weather'][0]['main'],  # p.ex. 'Clear', 'Rain'
        'icon': data['weather'][0]['icon']
    })
