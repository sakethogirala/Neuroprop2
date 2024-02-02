from django.shortcuts import render, redirect
from .utils import get_data_from_api, main
from .models import Data
import json
import os
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger
from .tasks import *

def refresh_data(request):
    filename = get_data_from_api()
    main.delay(filename, samples=10000000)
    return redirect("get_preds")

def get_preds(request):
    data = Data.objects.all()
    final_data = [json.loads(entry.data) for entry in data]
    data_elements = []
    for entry in final_data:
        for index in range(len(entry['loanuniversepropid'])):
            temp = []
            temp.append(entry['loanuniversepropid'][index])
            temp.append(entry['propname'][index])
            temp.append(entry['city'][index])
            temp.append(entry['secloanbal'][index])
            temp.append(entry['predictions'][index])
            data_elements.append(temp)
    if len(data_elements) == 0:
        messages.info(request, "There are no Historical Predection Data Found!")
        return render(request, 'prospect.html')

    # # Sort the data by 'predictions' in descending order (replace `reverse=True` with `reverse=False` if you want ascending order)
    # data_elements.sort(key=lambda x: x['predictions'], reverse=True)
    # data_elements = data_elements[:100]

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

