from django.urls import path
from . import views

app_name = 'ml'

urlpatterns = [
    # Page to input soil data and see crop result [cite: 1252]
    path('recommend-crop/', views.crop_recommend_view, name='crop_recommend'),
    
    # Page for yield estimation [cite: 1258]
    path('predict-yield/', views.yield_predict_view, name='yield_predict'),
]