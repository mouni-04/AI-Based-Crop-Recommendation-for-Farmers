from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import login_view, logout_view, signup_view, verify_otp_view, user_directory_view, admin_dashboard_view, toggle_user_status
app_name = 'accounts'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),

    path('', include('django.contrib.auth.urls')),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('user-directory/', user_directory_view, name='user_directory'),
    path('user-directory/toggle/<int:user_id>/', toggle_user_status, name='toggle_user_status'),

    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html'
        ),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
