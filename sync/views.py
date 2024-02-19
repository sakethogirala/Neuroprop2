from django.shortcuts import render, HttpResponse


def email_webhook(request):
    if request.method == "POST":
        print(request.POST)
        return HttpResponse("Hello World")