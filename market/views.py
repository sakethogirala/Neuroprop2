from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import re

@login_required
def lender_map(request):
    lenders = Lender.objects.all()
    context = {
        "lenders": lenders
    }
    return render(request, "market/lender-map.html", context)

@login_required
def lenders(request):
    query = Lender.objects.all()

    # Filtering by loan amount
    loan_amount_str = request.GET.get('loan_amount')
    if loan_amount_str:
        loan_amount = float(re.sub(r'[^\d.]', '', loan_amount_str))
        query = query.filter(data__min_loan__lte=loan_amount, data__max_loan__gte=loan_amount)

    # Filtering by property type
    property_type = request.GET.get('property_type')
    if property_type:
        print("property type")
        query = query.filter(data__property_types__contains=[property_type])

    # Filtering by state
    state = request.GET.get('state')
    if state:
        query = query.filter(data__states__contains=[state])

    context = {
        "lenders": query,
        "states": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
        "property_types": ["RT", "OF", "IN", "WH", "MF", "LO", "HC", "SS", "MU", "MH", "CH", "OT"]
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


def render_offcanvas(request):
    lender_pk = request.GET.get('lender_pk')
    lender = Lender.objects.get(pk = lender_pk)
    return render(request, 'includes/lender-offcanvas-body.html', {'lender': lender})

from django.shortcuts import redirect
from .models import Note  # Adjust the import according to your app

def add_note(request):
    if request.method == 'POST':
        print(request.POST)
        note_text = request.POST.get('noteText')
        lender_pk = request.POST.get("lender_pk")
        note_file = request.FILES.get('noteFile') if 'noteFile' in request.FILES else None
        lender = get_object_or_404(Lender, pk = lender_pk)
        new_note = Note(lender = lender, text=note_text, file=note_file, user=request.user)  # Adjust fields as needed
        new_note.save()

        messages.success(request, f"Note added to {lender.title}")
        return redirect("lenders")

    # If not POST, redirect to some page or show an error
    messages.error(request, "error creating note.")
    return redirect("lenders")
