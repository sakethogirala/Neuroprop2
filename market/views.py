from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.http import JsonResponse
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from prospect.models import Prospect
import re
import json
from django.urls import reverse
from django.template.loader import render_to_string

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
    context = {
        "lenders": query,
        "states": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
        "property_types": OUTREACH.PROPERTY_TYPES,
        "prospects": Prospect.objects.filter(users=request.user)
    }
    return render(request, "market/lenders.html", context)

def lenders_search(request):
    print(request.GET)
    query = Lender.objects.all()
    name = request.GET.get('name')
    if name:
        query = query.filter(data__title__icontains=name)
    
    loan_amount_str = request.GET.get('loan_amount')
    if loan_amount_str:
        loan_amount = float(re.sub(r'[^\d.]', '', loan_amount_str))
        query = query.filter(data__min_loan__lte=loan_amount, data__max_loan__gte=loan_amount)

    property_type = request.GET.get('property_type')
    if property_type:
        query = query.filter(data__property_types__contains=[property_type])

    state = request.GET.get('state')
    if state:
        query = query.filter(data__states__contains=[state])
    print(len(query))
    html = render_to_string("includes/lenders-table.html", context={"lenders": query})
    return JsonResponse({"html": html}, safe=False)


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

def delete_lender(request, lender_pk):
    if request.user.staff_access():
        lender = get_object_or_404(Lender, pk = lender_pk)
        lender.delete()
        messages.success(request, "Lender deleted.")
    else:
        messages.error(request, "You do not have access to remove lenders.")
    return redirect("lenders")

def edit_lender(request, lender_pk):
    lender = get_object_or_404(Lender, pk = lender_pk)
    if request.method == "POST":
        data = request.POST
        title = data.get("title")
        contact = data.get("contact")
        max_loan = float(data.get("max_loan"))
        min_loan = float(data.get("min_loan"))
        max_ltv = data.get("max_ltv")
        property_types = data.getlist("property_types[]")
        states = data.getlist("states[]")
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
        lender.data = data
        lender.title = data.get("title")
        lender.save()
        messages.success(request, "Lender edited!")
        return redirect("lenders")
    context = {
        "lender": lender,
        "states": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
        "property_types": OUTREACH.PROPERTY_TYPES
    }
    return render(request, "market/edit-lender.html", context)

@login_required
def create_outreach(request):
    if request.method == "POST":
        lenders_string = request.POST.get('lenders')
        selected_lender_ids = lenders_string.split(',') if lenders_string else []

        selected_lenders = Lender.objects.filter(id__in=selected_lender_ids)
        prospect = get_object_or_404(Prospect, uid = request.POST.get("prospect_uid"))
        new_outreach = Outreach.objects.create(
            name=f'{prospect.name} Outreach',
            created_by=request.user,
            status='planned',
            prospect=prospect,
        )

        new_outreach.lenders.set(selected_lenders)
        new_outreach.save()

        return redirect(reverse("outreach_detail", kwargs={"outreach_uid": new_outreach.uid}))

    return redirect("lenders")

def outreaches(request):
    outreaches = Outreach.objects.filter(created_by = request.user).order_by("-created_at")
    context = {
        "outreaches": outreaches,
    }
    return render(request, "market/outreaches.html", context)

def outreach_detail(request, outreach_uid):
    outreach = get_object_or_404(Outreach, uid = outreach_uid)
    context = {
        "outreach": outreach,
        "prospect": outreach.prospect
    }
    return render(request, "market/outreach-detail.html", context)