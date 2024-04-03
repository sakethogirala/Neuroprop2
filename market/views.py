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
from django.utils import timezone
import openai
from .tasks import openai_generate_outreach, send_outreach_emails

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

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
        contact_email = data.get("contact_email")
        contact_name = data.get("contact_name")
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
                "contact_email": contact_email,
                "contact_name": contact_name,
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
        name = request.POST.get("name", None)
        selected_lender_ids = lenders_string.split(',') if lenders_string else []

        selected_lenders = Lender.objects.filter(id__in=selected_lender_ids)
        prospect = get_object_or_404(Prospect, uid=request.POST.get("prospect_uid"))

        existing_outreach_count = Outreach.objects.filter(prospect=prospect).count()

        if existing_outreach_count > 0:
            if not name:
                name = f'{prospect.name} Outreach #{existing_outreach_count + 1}'
            else:
                existing_similar_names = Outreach.objects.filter(name__startswith=name, prospect=prospect).count()
                if existing_similar_names > 0:
                    name = f"{name} #{existing_similar_names + 1}"
        else:
            name = f'{prospect.name} Outreach' if not name else name

        new_outreach = Outreach.objects.create(
            name=name,
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

@login_required
def remove_lender(request, outreach_pk, lender_pk):
    outreach = get_object_or_404(Outreach, pk = outreach_pk)
    lender = get_object_or_404(Lender, pk = lender_pk)
    outreach.lenders.remove(lender)
    return redirect(reverse("outreach_detail", kwargs={"outreach_uid": outreach.uid}))

@login_required
def generate_smart_outreach(request, outreach_pk):
    print("working")
    if request.user.staff_access():   
        outreach = get_object_or_404(Outreach, pk = outreach_pk)
        # file_ids = outreach.prospect.get_approved_documents()
        # print("FILE IDS: ", file_ids)
        # start_openai_smart_outreach.delay(outreach_pk)
        outreach.email_content = None
        openai_generate_outreach.delay(outreach_pk)
        outreach.openai_outreach_time_start = timezone.now()
        outreach.save()
        return redirect(reverse("outreach_detail", kwargs={"outreach_uid": outreach.uid}))
    
@login_required
def delete_outreach(request, outreach_pk):
    print("working")
    if request.user.staff_access():   
        outreach = get_object_or_404(Outreach, pk = outreach_pk)
        outreach.delete()
        return redirect("outreaches")

@login_required
def send_outreach(request, outreach_pk):
    if request.user.staff_access() and request.method == "POST":
        outreach = get_object_or_404(Outreach, pk = outreach_pk)
        data = request.POST
        print(data)
        # subject = data.get("subject")
        # schedule_call_url = data.get("schedule-call-url")
        # outreach.email_subject = subject
        # outreach.schedule_call_url = schedule_call_url
        outreach.status = "in_progress"
        outreach.save()
        send_outreach_emails.delay(outreach_pk)
        messages.success(request, "Emails are being sent now...")
        return redirect(reverse("outreach_detail", kwargs={"outreach_uid": outreach.uid}))
    
def save_outreach(request, outreach_pk):
    outreach = get_object_or_404(Outreach, pk = outreach_pk)
    print("saving outreach")
    data = request.POST
    print("PROPERTY DATA: ", data)
    print(data.get("property-image"))
    property_image = data.get("property-image")
    if property_image:
        outreach.email_image = Document.objects.get(pk = data.get("property-image"))
    print("1")
    outreach.email_subject = data.get("email-subject")
    print(outreach.email_subject)
    outreach.schedule_call_url = data.get("schedule-call-url")
    outreach.email_content = data.get("email-content")
    outreach.save()
    return HttpResponse("success", status = "200")

def view_outreach_preview(request, outreach_pk):
    print("working...")
    if request.user.staff_access():
        print("hello")
        outreach = get_object_or_404(Outreach, pk = outreach_pk)
        context = {
            "outreach": outreach,
            "lender": outreach.lenders.all().first(),
            "preview": True
        }
        body_html = render_to_string("emails/outreach-content.html", context)
        print(body_html)
        return JsonResponse({"html": body_html}, safe=False)
