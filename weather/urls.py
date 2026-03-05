from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    # Main weather dashboard with cards and heatmap
    path('dashboard/', views.weather_dashboard_view, name='weather_dashboard'),
]