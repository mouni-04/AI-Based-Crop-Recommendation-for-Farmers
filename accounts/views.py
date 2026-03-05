from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from .models import EmailOTP
from ml.models import CropRecommendationLog
import random
from django.utils import translation

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user:
            if not user.is_active:
                messages.error(request, 'Please verify your email first.')
                return render(request, 'accounts/login.html')

            login(request, user)
            user.login_count += 1
            user.save()
            return redirect('landing')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')


def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.info(request, 'User already exists. Please login.')
            return redirect('accounts:login')

        user = User.objects.create_user(
            email=email,
            password=password,
            is_active=False
        )

        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})

        send_mail(
            'Verify your account',
            f'Your OTP code is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        request.session['verify_user'] = user.id
        return redirect('accounts:verify_otp')

    return render(request, 'accounts/signup.html')


def verify_otp_view(request):
    user_id = request.session.get('verify_user')
    if not user_id:
        return redirect('accounts:signup')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_obj = EmailOTP.objects.filter(user=user).first()

        if otp_obj and not otp_obj.is_expired() and entered_otp == otp_obj.otp:
            user.is_active = True
            user.is_verified = True
            user.save()
            otp_obj.delete()
            del request.session['verify_user']
            return render(request, 'accounts/verify_success.html')

        messages.error(request, 'Invalid or expired OTP.')

    return render(request, 'accounts/verify_otp.html')


def logout_view(request):
    logout(request)
    return redirect('landing')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard_view(request):
    """
    Aggregates real-time metrics for the Command Center.
    """
    # 1. KPI Calculations
    total_users = User.objects.filter(is_superuser=False).count()
    total_logs = CropRecommendationLog.objects.count()
    total_yields = YieldPredictionLog.objects.count()
    
    # 2. Recent Inference Activity (Last 5)
    recent_logs = CropRecommendationLog.objects.select_related('user').order_by('-timestamp')[:5]
    
    # 3. Language/Regional Demand (Mock logic or real if you track profile language)
    # For now, we assume these distribution stats
    regional_stats = {
        'hindi': 45,
        'telugu': 35,
        'english': 20
    }

    context = {
        'total_users': total_users,
        'total_logs': total_logs,
        'total_yields': total_yields,
        'recent_logs': recent_logs,
        'regional_stats': regional_stats,
        'page_title': 'Admin Command Center'
    }
    
    return render(request, 'dashboards/admin_dashboard.html', context)

@login_required
def user_directory_view(request):
    """Logic for the Farmer Node Directory"""
    if not request.user.is_superuser:
        return redirect('user_dashboard')

    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'dashboards/user_directory.html', {'users': users})

@login_required
def toggle_user_status(request, user_id):
    """Admin tool to activate/deactivate a farmer node"""
    if not request.user.is_superuser:
        return redirect('accounts:landing')
    
    target_user = get_object_or_404(User, id=user_id)
    target_user.is_active = not target_user.is_active
    target_user.save()
    
    status = "activated" if target_user.is_active else "suspended"
    messages.success(request, f"Farmer node {target_user.email} has been {status}.")
    return redirect('accounts:user_directory')

@login_required
def profile_settings_view(request):
    user = request.user
    
    # 1. Logic for Dynamic System Role display
    # This ensures "ROOT_ADMIN" or "VERIFIED_FARMER" is sent to the HTML
    display_role = "ROOT_ADMIN" if user.is_superuser else "VERIFIED_FARMER"

    if request.method == 'POST':
        # Handle Profile Update (Email)
        if 'email' in request.POST:
            new_email = request.POST.get('email')
            if new_email:
                user.email = new_email
                user.save()
                messages.success(request, "Your account identity has been updated!")
            else:
                messages.error(request, "Invalid email address provided.")
        
        # Handle Language Switching (Dropdown)
        if 'language' in request.POST:
            lang_code = request.POST.get('language')
            translation.activate(lang_code)
            request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
            messages.success(request, "Language preferences updated!")
        
        return redirect('accounts:profile_settings')

    # Pass the context to the template
    context = {
        'display_role': display_role,
    }
    return render(request, 'dashboards/profile.html', context)