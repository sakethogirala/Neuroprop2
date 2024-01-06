from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.core.files.storage import FileSystemStorage
from .models import Prospect, Document, DocumentType
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

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

class TrackerMain(ListView):
    model = Prospect
    paginate_by = 20  # if pagination is desired
    template_name = "tracker-main.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.model.objects.all().count()
        context["purpose_choices"] = PROSPECT.PURPOSE_CHOICES
        context["property_type_choices"] = PROSPECT.PROPERTY_TYPE_CHOICES
        return context

def tracker_detail(request, prospect_pk, document_type_pk):
    prospect = get_object_or_404(Prospect, pk = prospect_pk)
    document_type = get_object_or_404(DocumentType, pk = document_type_pk)
    context = {
        "prospect": prospect,
        "current_document_type": document_type,
    }
    if request.user.account_type == "user":
        return render(request, "tracker-detail-client.html", context = context)

    return render(request, "tracker-detail-staff.html", context = context)
    
def upload_document(request):
    print(request.POST)
    print(request.FILES)
    if request.method == 'POST' and request.FILES['file']:
        document_file = request.FILES.get('file')
        document_type_pk = request.POST.get("document_type_pk")
        document_type = get_object_or_404(DocumentType, pk = document_type_pk)
        document = Document.objects.create(document_type = document_type)
        document.file = document_file
        document.name = f"{document_type.general_name}_{document_type.document_count}"
        document.save()
        document_type.document_count += 1
        document_type.save()
        print(document)
        # # Start AI Review
        document.openai_upload_file(client)
        document.openai_check_start(client)
        # document.openai_feedback_start(client)
        response = {
            "status": "success",
            "document_pk": document.pk
        }
        return JsonResponse(response, safe=False)
        messages.success(request, "File uploaded. Checking File...")
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": document_type.prospect.pk, "document_type_pk": document_type_pk}))
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
        if request.user.is_staff or (request.user in document.prospect.users.all()):
            return FileResponse(document.file.open(), as_attachment=True, filename=f"{document.name}.pdf")
    raise Http404()

def get_openai_get_file_check(request):
    print("getting file check status...")
    document_pk = request.GET.get("document_pk")
    document = get_object_or_404(Document, pk = document_pk)
    feedback = document.openai_get_result(client, document.openai_check_thread_id, document.openai_check_run_id)

    if not feedback:
        return JsonResponse({"status": "pending"}, safe=False)
    
    feedback = feedback
    print("loading...")
    print(feedback)
    document.feedback = feedback["feedback"]
    if feedback["correct"]:
        print("APPROVED")
        document.status = "approved"
    if not feedback["correct"]:
        print("rejected")
        document.status = "rejected"
        document.client_feedback = feedback["feedback"]
    document.file_checked = True
    document.save()
    feedback["status"] = "success"
    return JsonResponse(data=feedback, safe=False)


def send_to_user(request):
    # Get data and objects
    data = request.POST
    email = data.get("email")
    prospect_pk = data.get("prospect-pk")
    prospect = get_object_or_404(Prospect, pk = prospect_pk)
    # create new user from email entered
    existing_user = get_user_model().objects.filter(email = email)
    if existing_user.exists():
        print("user already exists adding them")
        prospect.users.add(existing_user.first())
        # Send email showing with new link and permission
        messages.success(request, "User already exists. Adding them to project.")
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect_pk, "document_type_pk": prospect.get_next_document_type()}))
    new_user = get_user_model().objects.create(email = email, account_type = "user", password = "neuroprop", is_allowed = False)
    # send email to user to login, change password, etc
    new_user.send_password_set_email(request)
    # grant this user permission to be on prospect
    prospect.users.add(new_user)
    messages.success(request, f"Sent {email} NeuroProp account login for this project.")
    return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect_pk, "document_type_pk": prospect.get_next_document_type()}))

def remove_user(request):
    prospect_uid = request.GET.get("prospect_uid")
    target_user_pk = request.GET.get("target_user_pk")

    user = get_object_or_404(get_user_model(), pk = target_user_pk)
    prospect = get_object_or_404(Prospect, uid = prospect_uid)
    if user == request.user:
        messages.error(request, f"You can't remove yourself.")
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect.pk, "document_type_pk": prospect.get_next_document_type()}))
    if request.user.is_staff or (request.user in prospect.users.all()):
        prospect.users.remove(user)
        messages.error(request, f"Removed user's access.")
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect.pk, "document_type_pk": prospect.get_next_document_type()}))


def override_document_check(request, document_uid):
    document = get_object_or_404(Document, uid = document_uid)
    document_type_pk = document.document_type.pk
    document.status = "approved"
    document.overridden = True
    document.save()
    return redirect(reverse("tracker-detail", kwargs={"prospect_pk": document.document_type.prospect.pk, "document_type_pk": document_type_pk}))

@login_required
def create_prospect(request):
    if request.method == "POST":
        data = request.POST
        print(data)
        name = data.get("name")
        purpose = data.get("purpose")
        property_type= data.get("property-type")
        amount = data.get("amount")
        prospect = Prospect.objects.create(
            name = name,
            purpose = purpose,
            property_type = property_type,
            amount = amount
        )
        prospect.users.add(request.user)
        messages.success(request, "Prospect created!")
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": prospect.pk, "document_type_pk": prospect.get_next_document_type()}))
    return HttpResponse("error", status = "404")

@login_required
def delete_prospect(request, prospect_uid):
    if request.user.account_type != "user":
        prospect = get_object_or_404(Prospect, uid = prospect_uid)
        prospect.delete()
        return redirect("tracker-main")
    return HttpResponse("error", status = "404")

@login_required
def send_client_feedback(request):
    if request.user.account_type != "user":
        data = request.POST
        document_uid = data.get("document_uid")
        document = get_object_or_404(Document, uid = document_uid)
        feedback = data.get("feedback")
        document.client_feedback = feedback
        document.save()
        return redirect(reverse("tracker-detail", kwargs={"prospect_pk": document.document_type.prospect.pk, "document_type_pk": document.document_type.pk}))
    return HttpResponse("error", status = "404")
