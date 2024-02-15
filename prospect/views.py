from django.shortcuts import render, redirect
from .utils import get_data_from_api
from .models import Data
import json
import os
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger
from .tasks import *

def refresh_data(request):
    # filename = get_data_from_api()
    process_and_store_data.delay()
    return redirect("get_preds")

def get_preds(request):
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
    return render(request, "prospect.html", {'data': page_obj})

