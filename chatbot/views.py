import json
import base64
import re
import google.generativeai as genai

from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import ChatConversation

# ---------------------------------------------------
# Gemini Configuration
# ---------------------------------------------------
genai.configure(api_key=settings.AI_API_KEY)


# ---------------------------------------------------
# Utility: Clean Markdown from AI Output
# ---------------------------------------------------
def clean_markdown(text):
    if not text:
        return ""

    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'-\s+', '• ', text)
    return text.strip()


# ---------------------------------------------------
# Language Detection
# ---------------------------------------------------
def detect_language(text):
    if not text:
        return None

    # Telugu
    if re.search(r'[\u0C00-\u0C7F]', text):
        return "te"

    # Hindi
    if re.search(r'[\u0900-\u097F]', text):
        return "hi"

    # Default English
    return "en"


# ---------------------------------------------------
# Page View
# ---------------------------------------------------
def full_chat_view(request):
    return render(request, 'chatbot/chatbot.html')


# ---------------------------------------------------
# Chatbot API Endpoint
# ---------------------------------------------------
@csrf_exempt
def chatbot_query(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body)

        user_msg = data.get('msg', '').strip()
        image_data = data.get('image')

        # ---------------- Language Detection ----------------
        detected_lang = detect_language(user_msg)

        if detected_lang:
            request.session["chat_language"] = detected_lang

        lang = request.session.get("chat_language", "en")

        # ---------------- Gemini Model ----------------
        model = genai.GenerativeModel("gemini-2.5-flash")

        # ---------------- Language Lock Prompt ----------------
        language_instruction = {
            "en": "You MUST reply ONLY in English.",
            "hi": "आपको उत्तर केवल हिंदी में देना है। अंग्रेज़ी या तेलुगु का उपयोग न करें।",
            "te": "మీరు తప్పనిసరిగా తెలుగులోనే సమాధానం ఇవ్వాలి. ఇంగ్లీష్ లేదా హిందీ ఉపయోగించవద్దు."
        }[lang]

        system_prompt = f"""
You are AgriExpert AI, a professional agricultural advisor.

{language_instruction}

Capabilities:
- Answer farming questions
- Analyze crop images
- Suggest remedies and fertilizers
- Recommend consulting experts when risk is high

Rules:
- Plain text only
- Structured responses
- If image is provided, prioritize image analysis
- If disease detected, include: Name, Cause, Remedy, Prevention
"""

        # ---------------- Build Multimodal Input ----------------
        contents = [system_prompt]

        if image_data:
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]

            image_bytes = base64.b64decode(image_data)
            contents.append({
                "mime_type": "image/jpeg",
                "data": image_bytes
            })

        if user_msg:
            contents.append(user_msg)

        if len(contents) <= 1:
            return JsonResponse({
                'reply': 'Please describe your concern or upload a crop photo.'
            })

        # ---------------- Generate Response ----------------
        response = model.generate_content(contents)
        raw_reply = response.text or "Unable to process the request."

        bot_reply = clean_markdown(raw_reply)

        # ---------------- Save Conversation ----------------
        ChatConversation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            message=user_msg or "[Image Uploaded]",
            response=bot_reply,
            is_anonymous=not request.user.is_authenticated
        )

        return JsonResponse({
            "reply": bot_reply,
            "status": "success"
        })

    except Exception as e:
        print("Chatbot Logic Error:", str(e))
        return JsonResponse(
            {'reply': 'Satellite link interrupted. Please try again.'},
            status=500
        )
