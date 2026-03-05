from django.urls import path
from . import views

app_name = 'schemes'

urlpatterns = [
    path('list/', views.scheme_list_view, name='scheme_list'),
    path('import/', views.bulk_upload_view, name='bulk_upload'), # Add this
]