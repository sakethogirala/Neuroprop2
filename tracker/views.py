from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.core.files.storage import FileSystemStorage
from .models import Prospect, Document, DocumentType
from prospect.models import Address
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import Http404, FileResponse
from django.contrib.auth import get_user_model
import openai
from django.conf import settings
from django.http import JsonResponse, HttpResponse
import json
from django.contrib.auth.decorators import login_required
from prospect import PROSPECT
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from . import DOCUMENT, DOCUMENT_TYPE
from django.db.models import Q
from .tasks import *
from django.contrib.auth.mixins import LoginRequiredMixin

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

class TrackerMain(LoginRequiredMixin, ListView):
    model = Prospect
    ordering = ["-created_at"]
    paginate_by = 20  # if pagination is desired
    template_name = "tracker-main.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.model.objects.all().count()
        context["purpose_choices"] = PROSPECT.PURPOSE_CHOICES
        context["property_type_choices"] = PROSPECT.PROPERTY_TYPE_CHOICES
        return context
    
@login_required
def tracker_main(request):
    prospects = Prospect.objects.filter(users=request.user).order_by("-created_at")
    context = {
        "object_list": prospects,
        "total": prospects.count(),
        "purpose_choices": PROSPECT.PURPOSE_CHOICES,
        "property_type_choices": PROSPECT.PROPERTY_TYPE_CHOICES
    }
    return render(request, "tracker-main.html", context)

def tracker_detail(request, prospect_pk, document_type_pk=None):
    prospect = get_object_or_404(Prospect, pk = prospect_pk)
    is_staff = request.user.staff_access()

    if (not prospect.client_onboarded) and (not is_staff):
        return redirect(reverse("onboard_client", kwargs={"prospect_uid": prospect.uid}))

    if not document_type_pk:
        document_type = get_object_or_404(DocumentType, pk = prospect.get_next_document_type())
    else:
        document_type = get_object_or_404(DocumentType, pk = document_type_pk)


    if is_staff:
        document_types = prospect.document_types.all()
        pipeline = Document.objects.filter(document_type__prospect=prospect).filter(Q(status = "pending") | Q(client_question__isnull=False))
    else:
        document_types = prospect.document_types.exclude(status="hidden")
        pipeline = Document.objects.filter(document_type__prospect=prospect, status="rejected")

    context = {
        "is_staff": is_staff,
        "prospect": prospect,
        "current_document_type": document_type,
        "document_types": document_types,
        "pipeline": pipeline,
        "DOCUMENT_TYPE_STATUS_CHOICES": DOCUMENT_TYPE.STATUS_CHOICES
    }
    return render(request, "tracker-detail.html", context = context)

def upload_document(request):
    if request.method == 'POST' and request.FILES['file']:
        document_file = request.FILES.get('file')
        document_type_pk = request.POST.get("document_type_pk")
        document_type = get_object_or_404(DocumentType, pk = document_type_pk)
        print(document_type)
        # Handle images
        if document_type.is_image:
            document_type.status = "pending"
            document = Document.objects.create(document_type = document_type)
            document.uploaded_by = request.user
            document.file = document_file
            document.name = f"{document_type.general_name}_{document_type.document_count}"
            document.smart_checked = True
            document.save()
            response = {
                "status": "success",
                "document_pk": document.pk
            }
            return JsonResponse(response, safe=False)

        if document_type.status == "not_uploaded":
            document_type.status = "pending"
            document_type.save()
        document = Document.objects.create(document_type = document_type)
        document.uploaded_by = request.user
        document.file = document_file
        document.name = f"{document_type.general_name}_{document_type.document_count}"
        document.save()

        document_type.document_count += 1
        document_type.save()

        
        print("right here")
        # # Start AI Review
        document.openai_upload_file(client)
        print("uploaded here")
        # Start async document check
        start_openai_document_feedback.delay(document.pk)
        print("started celery document feedback")
        response = {
            "status": "success",
            "document_pk": document.pk
        }
        return JsonResponse(response, safe=False)
    raise Http404()

def delete_document(request, document_uid):
    print(document_uid)
    document = get_object_or_404(Document, uid = document_uid)
    print(document)
    document_type_pk = document.document_type.pk
    document.delete()
    return redirect(reverse("tracker-detail", kwargs={"prospect_pk": document.document_type.prospect.pk, "document_type_pk": document_type_pk}))


def download_document(request):
    if request.method == "GET":
        document_uid = request.GET.get("document_uid")
        print(document_uid)
        document = get_object_or_404(Document, uid = document_uid)
        if request.user.staff_access() or (request.user in document.prospect.users.all()):
            return FileResponse(document.file.open(), as_attachment=True, filename=f"{document.name}.pdf")
    raise Http404()


def send_to_user(request):
    data = request.POST
    email = data.get("email")
    prospect_pk = data.get("prospect-pk")
    prospect = get_object_or_404(Prospect, pk = prospect_pk)
    existing_user = get_user_model().objects.filter(email = email)
    if existing_user.exists():
        print("user already exists adding them")
        prospect.users.add(existing_user.first())
        messages.success(request, "User already exists. Adding them to project.")
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect_pk, "document_type_pk": prospect.get_next_document_type()}))
    new_user = get_user_model().objects.create(email = email, account_type = "user", password = "neuroprop", is_allowed = False)
    # send email to user to login, change password, etc
    new_user.send_password_set_email(request)
    prospect.users.add(new_user)
    messages.success(request, f"Sent {email} NeuroProp account login for this project.")
    return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect_pk, "document_type_pk": prospect.get_next_document_type()}))

def remove_user(request):
    prospect_uid = request.GET.get("prospect_uid")
    target_user_pk = request.GET.get("target_user_pk")
    user = get_object_or_404(get_user_model(), pk = target_user_pk)
    prospect = get_object_or_404(Prospect, uid = prospect_uid)
    if user.staff_access():
        messages.error(request, "Staff cannot be removed.")
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect.pk, "document_type_pk": prospect.get_next_document_type()}))
    if user == request.user:
        messages.error(request, f"You can't remove yourself.")
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect.pk, "document_type_pk": prospect.get_next_document_type()}))
    if request.user.staff_access() or (request.user in prospect.users.all()):
        prospect.users.remove(user)
        messages.error(request, f"Removed user's access.")
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect.pk, "document_type_pk": prospect.get_next_document_type()}))

def override_document_check(request, document_uid):
    document = get_object_or_404(Document, uid = document_uid)
    document_type_pk = document.document_type.pk
    document.status = "pending"
    document.overridden = True
    document.save()
    return redirect(reverse("tracker-detail", kwargs={"prospect_pk": document.document_type.prospect.pk, "document_type_pk": document_type_pk}))

@login_required
def create_prospect(request):
    if request.method == "POST":
        data = request.POST
        print(data)
        address = Address.objects.create(address=data.get("address"), address2=data.get("address2"), city=data.get("locality"), state=data.get("state"), postal_code=data.get("postcode"), country=data.get("country"))
        name = data.get("name")
        purpose = data.get("purpose")
        property_type= data.get("property-type")
        amount = data.get("amount")
        prospect = Prospect.objects.create(
            created_by = request.user,
            name = name,
            purpose = purpose,
            property_type = property_type,
            amount = amount,
            address = address
        )
        prospect.users.add(request.user)
        messages.success(request, "Prospect created!")
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect.pk, "document_type_pk": prospect.get_next_document_type()}))
    context = {
        "purpose_choices": PROSPECT.PURPOSE_CHOICES,
        "property_type_choices": PROSPECT.PROPERTY_TYPE_CHOICES
    }
    return render(request, "create-prospect.html", context)

@login_required
def delete_prospect(request, prospect_uid):
    if request.user.staff_access():
        prospect = get_object_or_404(Prospect, uid = prospect_uid)
        prospect.delete()
        return redirect("tracker-main")
    return HttpResponse("error", status = "404")

@login_required
def send_client_feedback(request):
    if request.user.staff_access():
        data = request.POST
        action = data.get("action")
        document_uid = data.get("document_uid")
        document = get_object_or_404(Document, uid = document_uid)
        feedback = data.get("feedback")
        document.client_feedback = feedback
        document.client_question = None
        if action == "approve":
            document.status = "approved"
        if action == "reject":
            document.status = "rejected"
            document.overridden = True
            document.document_type.client_notifications = True
            document.notify_document_rejected()
            document.document_type.save()
            
            messages.success(request, f"Sent email to clients.")
        
        document.save()
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": document.document_type.prospect.pk, "document_type_pk": document.document_type.pk}))
    return HttpResponse("error", status = "404")

@login_required
def update_document_type_status(request):
    if request.method == "POST":
        data = request.POST
        document_type_pk = data.get("document_type_pk") 
        status = data.get("status")
        document_type = get_object_or_404(DocumentType, pk = document_type_pk)
        document_type.status = status
        document_type.save()
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": document_type.prospect.pk, "document_type_pk": document_type.pk}))
    return HttpResponse("error", status = "404")


def poll_openai_document_check(request):
    print("getting file check status...")
    document_pk = request.GET.get("document_pk")
    document = get_object_or_404(Document, pk = document_pk)
    if document.openai_feedback_time:
        return JsonResponse({"status": "success"}, safe=False)
    else:
        return JsonResponse({"status": "pending"}, safe=False)


def openai_sort_document(request):
    pass

def replace_document(request):
    pass

@login_required
def ask_document_question(request):
    if request.method == "POST":
        data = request.POST
        question = data.get("question")
        document_uid = data.get("document_uid")
        document = get_object_or_404(Document, uid = document_uid)
        document.client_question = question
        document.save()
        subject = f"Client asked question"
        location = reverse("tracker-detail", kwargs={"prospect_pk": document.document_type.prospect.pk, "document_type_pk": document.document_type.pk})
        link = "https://neuroprop.com" + location
        # link = "http://127.0.0.1:8000" + location
        context = {"link": link, "document": document}
        html = render_to_string("emails/comment-added.html", context)
        print(html)
        txt = render_to_string("emails/comment-added.txt", context)
        email = send_mail(
            subject=subject,
            message=txt,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=document.document_type.prospect.created_by,
            html_message=html,
            fail_silently=False
        )
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": document.document_type.prospect.pk, "document_type_pk": document.document_type.pk}))
    return HttpResponse("error", status = "404")



@login_required
def edit_propsect(request, prospect_pk):
    prospect = get_object_or_404(Prospect, pk = prospect_pk)
    if request.method == "POST":
        data = request.POST
        prospect.name =  data.get("name")
        prospect.purpose = data.get("purpose")
        prospect.status = data.get("status")
        prospect.property_type= data.get("property-type")
        prospect.amount = data.get("amount")
        prospect.context = data.get("context")
        prospect.save()
        messages.success(request, "Prospect edited!")
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect.pk, "document_type_pk": prospect.get_next_document_type()}))
    context = {
        "prospect": prospect,
        "status_choices": PROSPECT.STATUS_CHOICES,
        "purpose_choices": PROSPECT.PURPOSE_CHOICES,
        "property_type_choices": PROSPECT.PROPERTY_TYPE_CHOICES
    }
    return render(request, "edit-prospect.html", context)


def onboard_client(request, prospect_uid):
    prospect = get_object_or_404(Prospect, uid = prospect_uid)
    if request.method == "POST":
        data = request.POST
        print(data)
        prospect.client_scenario = {
            "scenario": data.get("scenario"),
            "min_would_take": data.get("min"),
            "max_would_take": data.get("max")
        }
        prospect.client_onboarded = True
        prospect.save()
        messages.success(request, "Welcome to NeuroProp.")
    
    if prospect.client_onboarded:
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect.pk}))

    context = {

    }
    return render(request, "onboard-client.html", context)

@login_required
def smart_sort(request, prospect_pk):
    prospect = get_object_or_404(Prospect, pk = prospect_pk)
    print(request.POST)
    print(request.FILES)
    data = request.POST
    file = request.FILES.get("file")
    document = Document.objects.create(
        uploaded_by=request.user,
        file=file
    )
    start_openai_document_sort.delay(document.pk, prospect.pk)
    messages.success(request, "Your files are being smart sorted. We'll notify you once it's finished.")
    return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect.pk}))