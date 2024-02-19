from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def email_webhook(request):
    if request.method == "POST":
        print(request.POST)
        return HttpResponse("Hello World")