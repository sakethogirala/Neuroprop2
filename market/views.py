from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def lender_map(request):
    lenders = Lender.objects.all()
    context = {
        "lenders": lenders
    }
    return render(request, "market/lender-map.html", context)

def lenders(request):
    lenders = Lender.objects.all()
    context = {
        "lenders": lenders
    }
    return render(request, "market/lenders.html", context)

@login_required
def create_lender(request):
    if request.method == "POST":
        data = request.POST
        title = data.get("title")
        contact = data.get("contact")
        max_loan = "$" + data.get("max_loan")
        min_loan = "$" + data.get("min_loan")
        max_ltv = data.get("max_ltv") + "%"
        property_types = data.getlist("property_types[]")
        states = data.getlist("states[]")
        lender = Lender.objects.create(
            title = title,
            data = {
                "title": title,
                "type": "NA",
                "contact": contact,
                "max_loan": max_loan,
                "min_loan": min_loan,
                "max_ltv": max_ltv,
                "property_types": property_types,
                "states": states
            }
        )
        messages.success(request, "Lender added!")

        return redirect("lenders")
    return HttpResponse("error", status = "404")

