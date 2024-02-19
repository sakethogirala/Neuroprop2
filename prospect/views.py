from django.shortcuts import render, redirect
from .utils import get_data_from_api
import json
import os
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger
from .tasks import process_custom_data, process_and_store_data
from django.http import JsonResponse
from . models import ProspectData, DataUpload

def refresh_data(request):
    # filename = get_data_from_api()
    process_and_store_data.delay()
    return redirect("api_preds")

def api_preds(request):
    # data_elements = ProspectData.objects.order_by("-data__predictions")
    data_elements = ProspectData.objects.all()
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