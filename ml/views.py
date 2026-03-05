from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import CropRecommendationLog, YieldPredictionLog


@login_required
def crop_recommend_view(request):
    # Load ML dependencies only when the endpoint is actually called.
    try:
        from .utils import predict_crop
    except Exception as e:
        return render(request, 'ml/crop_recommend.html', {
            'error': f"ML models are currently unavailable: {str(e)}"
        })

    if request.method == 'POST':
        try:
            n = float(request.POST.get('n'))
            p = float(request.POST.get('p'))
            k = float(request.POST.get('k'))
            ph = float(request.POST.get('ph'))
            temp = float(request.POST.get('temp'))
            hum = float(request.POST.get('hum'))
            rain = float(request.POST.get('rainfall'))

            result, confidence = predict_crop(n, p, k, temp, hum, ph, rain)

            guidance_data = {
                'rice': 'Requires standing water and high nitrogen.',
                'maize': 'Requires well-drained soil and moderate rainfall.',
                'wheat': 'Requires cool weather and balanced nutrients.',
                'cotton': 'Needs warm temperature and deep soil.'
            }

            guidance = guidance_data.get(
                result.lower(),
                'Maintain proper soil moisture and monitor weather conditions.'
            )

            CropRecommendationLog.objects.create(
                user=request.user,
                n_value=n,
                p_value=p,
                k_value=k,
                ph_value=ph,
                temperature=temp,
                humidity=hum,
                rainfall=rain,
                recommended_crop=result
            )

            return render(request, 'ml/crop_recommend_result.html', {
                'result': result,
                'confidence': confidence,
                'guidance': guidance,
                'n': n,
                'p': p,
                'k': k,
                'ph': ph
            })

        except Exception as e:
            return render(request, 'ml/crop_recommend.html', {
                'error': f"System Error: {str(e)}"
            })

    # GET request → show form page
    return render(request, 'ml/crop_recommend.html')


@login_required
def yield_predict_view(request):
    # Load ML dependencies only when the endpoint is actually called.
    try:
        from .utils import predict_yield
    except Exception as e:
        return render(request, 'ml/yield_predict.html', {
            'error': f"ML models are currently unavailable: {str(e)}"
        })

    if request.method == 'POST':
        try:
            crop_type = request.POST.get('crop')
            season = request.POST.get('season')
            area = float(request.POST.get('area'))

            prediction_value = predict_yield(area, season, crop_type)

            YieldPredictionLog.objects.create(
                user=request.user,
                crop_name=crop_type,
                season=season,
                area=area,
                predicted_yield=prediction_value
            )

            return render(request, 'ml/yield_result.html', {
                'prediction': prediction_value,
                'crop': crop_type,
                'season': season,
                'area': area
            })

        except Exception as e:
            return render(request, 'ml/yield_predict.html', {
                'error': f'System Error: {str(e)}'
            })

    return render(request, 'ml/yield_predict.html')
