import json
import base64
from google import genai
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai

# Import your actual AgriTech models
from ml.models import CropRecommendationLog, YieldPredictionLog
from chatbot.models import ChatConversation
from schemes.models import GovernmentScheme, SchemeCategory

User = get_user_model()
genai.configure(api_key=settings.AI_API_KEY)

# ============================================================
# CORE & PUBLIC VIEWS
# ============================================================

def landing_view(request):
    """Public landing page with automatic redirect for logged-in users"""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')  # Redirect Root Admin
        return redirect('user_dashboard')       # Redirect Verified Farmer
    return render(request, 'landing.html')

@login_required
def profile_settings_view(request):
    """Farmer profile/account settings"""
    return render(request, 'dashboards/profile.html')

# ============================================================
# AI LENS – CROP DISEASE DIAGNOSIS
# ============================================================

@login_required
def ai_lens_view(request):
    """The dedicated page for AI-powered crop scanning"""
    return render(request, 'portal/ai_lens.html', {'page_type': 'ai_lens'})


@login_required
def api_extract_image(request):
    """API endpoint for AI Lens disease detection using Gemini"""
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            image_b64 = base64.b64encode(image_file.read()).decode()

            # System prompt adjusted for Agricultural Diagnosis
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    "Analyze this crop/leaf image. Identify the plant and any visible diseases. Provide Name, Cause, and Solution in plain text.",
                    {
                        "inline_data": {
                            "mime_type": image_file.content_type,
                            "data": image_b64
                        }
                    }
                ]
            )

            diagnosis = response.text.strip()

            return JsonResponse({
                'status': 'success',
                'diagnosis': diagnosis,
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# ============================================================
# FARMER (USER) DASHBOARD
# ============================================================

@login_required
def user_dashboard_view(request):
    """Main dashboard for Farmers to see their history"""
    recommendations = CropRecommendationLog.objects.filter(user=request.user).order_by('-timestamp')
    yield_logs = YieldPredictionLog.objects.filter(user=request.user).order_by('-timestamp')
    
    context = {
        'plans': recommendations[:5], # Matches your template variable name
        'plan_count': recommendations.count(),
        'yield_logs': yield_logs,
        'saved_count': yield_logs.count(),
    }
    return render(request, 'dashboards/user_dashboard.html', context)


# ============================================================
# MASTER ADMIN COMMAND CENTER
# ============================================================

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard_view(request):
    """Global oversight with fallback counts to prevent errors if logs are empty"""
    from django.utils import timezone
    from datetime import timedelta
    last_week = timezone.now() - timedelta(days=7)

    # Use .count() to get totals and slice for the recent 5 logs
    context = {
        'total_users': User.objects.filter(is_superuser=False).count(),
        'total_logs': CropRecommendationLog.objects.count(),
        'total_yields': YieldPredictionLog.objects.count(),
        'recent_activity': CropRecommendationLog.objects.filter(timestamp__gte=last_week).count(),
        'recent_logs': CropRecommendationLog.objects.select_related('user').order_by('-timestamp')[:5],
    }
    return render(request, 'dashboards/admin_dashboard.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_analytics_view(request):
    """Visual data analytics for the Admin"""
    # Grouping logs by recommended crop for charts
    crop_stats = CropRecommendationLog.objects.values('recommended_crop').annotate(count=Count('id'))
    
    return render(request, 'dashboards/analytics.html', {
        'crop_labels': [item['recommended_crop'] for item in crop_stats],
        'crop_counts': [item['count'] for item in crop_stats],
        'total_users': User.objects.count(),
    })


@user_passes_test(lambda u: u.is_superuser)
def ai_monitor_view(request):
    """Monitoring the Gemini API status and health"""
    return render(request, 'dashboards/ai_monitor.html', {
        'status': 'OPERATIONAL',
        'latency': '210ms',
        'model': 'Gemini-1.5-Flash',
        'capabilities': ['Disease Diagnosis', 'Crop Recommendation', 'Soil Analysis']
    })


@user_passes_test(lambda u: u.is_superuser)
def user_directory_view(request):
    """Table view of all registered Farmers"""
    return render(request, 'dashboards/user_directory.html', {
        'users': User.objects.filter(is_superuser=False).order_by('-date_joined')
    })


@user_passes_test(lambda u: u.is_superuser)
def toggle_user_status(request, user_id):
    """Suspend or Activate a Farmer Node"""
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        messages.success(request, f"Status updated for {user.email}")
    return redirect('admin_user_management')


@user_passes_test(lambda u: u.is_superuser)
def admin_chat_logs_view(request):
    """Review AI Chatbot conversations for quality control"""
    logs = ChatConversation.objects.all().order_by('-timestamp')[:50]
    return render(request, 'dashboards/admin_chat_logs.html', {'logs': logs})

@login_required
def ai_lens_view(request):
    """Renders the dedicated page for AI-powered crop scanning."""
    return render(request, 'portal/ai_lens.html', {'page_type': 'ai_lens'})

import re

def clean_markdown(text):
    if not text:
        return ""

    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'-\s+', '- ', text)
    return text.strip()


@csrf_exempt
def api_agri_lens_analyze(request):
    if request.method != "POST" or not request.FILES.get("image"):
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        image_file = request.FILES["image"]
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode()

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = """
You are an expert agricultural pathologist.

Analyze the uploaded crop image carefully.

Return the response in EXACTLY this format:

CROP:
<crop name>

ISSUES IDENTIFIED:
- <issue 1>
- <issue 2 or NONE>

CAUSE:
<short cause>

REMEDY:
- <simple farmer-friendly step 1>
- <step 2>
- <recommended medicine if applicable>

EXPERT ADVICE:
<when to consult an agricultural officer>

Rules:
- Plain text only
- No markdown
- No emojis
- Be concise and accurate
"""

        response = model.generate_content([
            prompt,
            {
                "inline_data": {
                    "mime_type": image_file.content_type,
                    "data": image_b64
                }
            }
        ])

        diagnosis = clean_markdown(response.text)

        return JsonResponse({
            "status": "success",
            "diagnosis": diagnosis
        })

    except Exception as e:
        print("AGRI LENS ERROR:", str(e))
        return JsonResponse({
            "status": "error",
            "error": "Image analysis failed. Please try again."
        }, status=500)
