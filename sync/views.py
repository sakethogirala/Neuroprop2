from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def email_webhook(request):
    if request.method == "POST":
        print("post: ", request.POST)
        print("body: ", request.body)
        return HttpResponse("Hello World")