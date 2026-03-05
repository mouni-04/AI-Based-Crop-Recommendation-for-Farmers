from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from portal import views as portal_views 

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')), 
    path('admin/', admin.site.urls),
]

urlpatterns += i18n_patterns(
    path('', portal_views.landing_view, name='landing'),
    
    # Farmer Dashboard Routes
    path('dashboard/', portal_views.user_dashboard_view, name='user_dashboard'),
    path('profile/', portal_views.profile_settings_view, name='profile_settings'),
    
    # Admin Command Center Routes
    path('admin-center/', portal_views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-center/analytics/', portal_views.admin_analytics_view, name='admin_analytics'),
    path('admin-center/users/', portal_views.user_directory_view, name='admin_user_management'),
    path('admin-center/users/toggle/<int:user_id>/', portal_views.toggle_user_status, name='toggle_user_status'),
    path('admin-center/ai-monitor/', portal_views.ai_monitor_view, name='ai_monitor'),
    path('admin-center/chat-logs/', portal_views.admin_chat_logs_view, name='admin_chat_logs'),
    
    # AI Lens Routes (Crop Disease Scanner)
    path('ai-lens/', portal_views.ai_lens_view, name='ai_lens'),

    # Other Agricultural Apps
    path('accounts/', include('accounts.urls')),
    path('schemes/', include('schemes.urls')),
    path('ml/', include('ml.urls')),
    path('weather/', include('weather.urls')),
    path('chatbot/', include('chatbot.urls', namespace='chatbot')),
    path("agri-lens/analyze/", portal_views.api_agri_lens_analyze, name="api_agri_lens_analyze"),
)