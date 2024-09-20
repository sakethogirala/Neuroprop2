from django.shortcuts import render, redirect
from .utils import get_data_from_api
import json
import os
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger
from .tasks import process_custom_data, process_and_store_data
from django.http import JsonResponse
from . models import Prospect, ProspectData, DataUpload
from .tasks import process_sreo_document
from django.views.generic.edit import UpdateView
from .forms import ProspectForm
from django.views.generic import ListView
from .models import SREOData
from django.db.models import Q
from .utils import get_access_token, get_similar_properties_from_api
from django.http import JsonResponse

class ProspectUpdateView(UpdateView):
    model = Prospect
    form_class = ProspectForm
    template_name = 'prospect/prospect_update.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        if 'sreo_document' in form.changed_data:
            self.object.process_sreo()
        return response

def refresh_data(request):
    # filename = get_data_from_api()
    process_and_store_data.delay()
    return redirect("api_preds")


def api_preds(request):
    # data_elements = ProspectData.objects.order_by("-data__predictions")
    data_elements = ProspectData.objects.all().order_by('created_at')
    pagination = Paginator(data_elements, 25)
    page_number = request.GET.get('page')
    
    if not page_number:
        page_number = 1
    try:
        page_obj = pagination.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = pagination.page(1)
    return render(request, "api-preds.html", {'data': page_obj})

def custom_data_preds(request):
    data_uploads = DataUpload.objects.filter(uploaded_by = request.user).order_by("-created_at")

    context = {
        "data_uploads": data_uploads
    }
    return render(request, "custom-data-preds.html", context)


def custom_data_preds_detail(request, data_upload_pk):
    data_uploads = ProspectData.objects.filter(upload__pk = data_upload_pk)

    context = {
        "data": data_uploads
    }
    return render(request, "custom-data-preds-detail.html", context)

def upload_custom_preds_data(request):
    print("uploading custom data...")
    file = request.FILES.get("file")
    data_upload = DataUpload.objects.create(
        uploaded_by = request.user,
        file = file
    )
    process_custom_data.delay(data_upload.pk)
    response = {
        "status": "success",
    }
    return JsonResponse(response, safe=False)

def get_similar_properties(request):
    property_id = request.GET.get('property_id')
    if not property_id:
        return JsonResponse({'error': 'Property ID is required'}, status=400)
    
    access_token = get_access_token()
    similar_properties = get_similar_properties_from_api(access_token, property_id)
    return JsonResponse(similar_properties, safe=False)

def similar_properties(request, property_id):
    access_token = get_access_token()
    similar_properties = get_similar_properties_from_api(access_token, property_id)
    
    # Filter options
    proximity = request.GET.get('proximity')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Apply filters
    filtered_properties = similar_properties
    if proximity:
        filtered_properties = [p for p in filtered_properties if p.get('distance', 0) <= float(proximity)]
    if min_price:
        filtered_properties = [p for p in filtered_properties if p.get('price', 0) >= float(min_price)]
    if max_price:
        filtered_properties = [p for p in filtered_properties if p.get('price', 0) <= float(max_price)]
    
    context = {
        'similar_properties': filtered_properties,
        'property_id': property_id,
        'proximity': proximity,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'similar_properties.html', context)

class SREODataListView(ListView):
    model = SREOData
    template_name = 'prospect/sreo_data_list.html'
    context_object_name = 'sreo_data'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        property_type = self.request.GET.get('property_type')
        min_units = self.request.GET.get('min_units')
        max_units = self.request.GET.get('max_units')
        min_value = self.request.GET.get('min_value')
        max_value = self.request.GET.get('max_value')

        if property_type:
            queryset = queryset.filter(property_type=property_type)
        if min_units:
            queryset = queryset.filter(number_of_units__gte=min_units)
        if max_units:
            queryset = queryset.filter(number_of_units__lte=max_units)
        if min_value:
            queryset = queryset.filter(estimated_current_market_value__gte=min_value)
        if max_value:
            queryset = queryset.filter(estimated_current_market_value__lte=max_value)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['property_types'] = SREOData.objects.values_list('property_type', flat=True).distinct()
        return context