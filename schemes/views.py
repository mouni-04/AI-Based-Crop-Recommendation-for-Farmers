import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import SchemeCategory, GovernmentScheme

@login_required
def scheme_list_view(request):
    """Renders the Government Schemes page for Farmers."""
    categories = SchemeCategory.objects.prefetch_related('schemes').all()
    context = {
        'categories': categories,
        'page_title': 'Government Schemes for Farmers'
    }
    return render(request, 'schemes/scheme_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def bulk_upload_view(request):
    """Handles the JSON file upload from the Bulk Upload UI."""
    if request.method == 'POST' and request.FILES.get('json_file'):
        json_file = request.FILES['json_file']
        
        try:
            data = json.load(json_file)
            for item in data:
                # 1. Get or Create Category
                category_obj, _ = SchemeCategory.objects.get_or_create(
                    name=item['category']
                )
                
                # 2. Create Scheme
                GovernmentScheme.objects.create(
                    category=category_obj,
                    title=item['title'],
                    description=item['description'],
                    eligibility=item['eligibility'],
                    benefits=item['benefits'],
                    official_link=item['official_link'],
                    is_active=item.get('is_active', True)
                )
            messages.success(request, "Dataset imported successfully into the neural pipeline!")
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f"Import Error: {str(e)}")
            
    return render(request, 'dashboards/bulk_upload.html')