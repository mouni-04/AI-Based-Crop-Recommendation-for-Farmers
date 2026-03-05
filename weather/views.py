import requests
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import WeatherLog

@login_required
def weather_dashboard_view(request):
    api_key = os.getenv('WEATHER_API_KEY')

    city = request.GET.get('city')
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    weather_data = None
    heatmap_intensity = 0

    try:
        # Priority 1: GPS-based location
        if lat and lon:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            )

        # Priority 2: Manual city search
        else:
            city = city or "Bengaluru"
            url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={city}&appid={api_key}&units=metric"
            )

        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code == 200:
            weather_data = {
                'city': data['name'],
                'temp': round(data['main']['temp'], 1),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'wind': round(data['wind']['speed'], 1),
                'rainfall': data.get('rain', {}).get('1h', 0)
            }

            heatmap_intensity = min(
                max((weather_data['temp'] / 50) * 100, 0),
                100
            )

            WeatherLog.objects.create(
                user=request.user,
                location_name=weather_data['city'],
                temperature=weather_data['temp'],
                humidity=weather_data['humidity'],
                description=weather_data['description']
            )

    except Exception as e:
        print("Weather API Error:", e)

    return render(request, 'weather/weather_dashboard.html', {
    'weather': weather_data,
    'current_temp': weather_data['temp'] if weather_data else None,
    'humidity': weather_data['humidity'] if weather_data else None,
    'wind': weather_data['wind'] if weather_data else None,
    'city': weather_data['city'] if weather_data else city,
    'heatmap_intensity': heatmap_intensity,
})