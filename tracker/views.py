from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.core.files.storage import FileSystemStorage
from .models import Prospect, Document
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import Http404, FileResponse
from django.contrib.auth import get_user_model
import openai
from django.conf import settings
from django.http import JsonResponse

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

class TrackerMain(ListView):
    model = Prospect
    paginate_by = 20  # if pagination is desired
    template_name = "tracker-main.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.model.objects.all().count()
        return context
    
class TrackerDetail(DetailView):
    model = Prospect
    template_name = "tracker-detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context
    
def upload_document(request):
    if request.method == 'POST' and request.FILES['file']:
        document_file = request.FILES.get('file')
        document_pk = request.POST.get("document_pk")
        document = get_object_or_404(Document, pk = document_pk)
        document.file = document_file
        document.feedback = None
        document.save()
        print(client)
        # Start AI Review
        document.openai_start_feedback(client)

        messages.success(request, "File uploaded. AI review started...")
        return redirect(reverse("tracker-detail", kwargs={"pk": document.prospect.pk}))
    raise Http404()

def delete_document(request):
    if request.method == "POST":
        document_uid = request.POST.get("document_uid")
        print(document_uid)
        document = get_object_or_404(Document, uid = document_uid)
        document.file.delete()
        return redirect(reverse("tracker-detail", kwargs={"pk": document.prospect.pk}))
    raise Http404()


def download_document(request):
    if request.method == "GET":
        document_uid = request.GET.get("document_uid")
        print(document_uid)
        document = get_object_or_404(Document, uid = document_uid)
        if request.user.is_staff or (request.user in document.prospect.users.all()):
            return FileResponse(document.file.open(), as_attachment=True, filename=f"{document.name}.pdf")
    raise Http404()


def get_openai_status(request):
    print("getting openai status...")
    document_pk = request.GET.get("document_pk")
    document = get_object_or_404(Document, pk = document_pk)
    feedback = document.openai_get_feedback(client)
    print("FEEDBACK: ", feedback)
    if not feedback:
        return JsonResponse({"status": "failed"}, safe=False)
    document.feedback = feedback
    document.save()
    data = {
        "status": "success",
        "message": feedback
    }
    print(data)
    return JsonResponse(data = data, safe=False)

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
        return redirect(reverse("tracker-detail", kwargs={"pk": prospect.pk}))
    
    new_user = get_user_model().objects.create(email = email, account_type = "user", password = "neuroprop", is_allowed = False)
    # send email to user to login, change password, etc
    new_user.send_password_set_email(request)
    # grant this user permission to be on prospect
    prospect.users.add(new_user)
    messages.success(request, f"Sent {email} NeuroProp account login for this project.")
    return redirect(reverse("tracker-detail", kwargs={"pk": prospect.pk}))

def remove_user(request):
    prospect_uid = request.GET.get("prospect_uid")
    target_user_pk = request.GET.get("target_user_pk")

    user = get_object_or_404(get_user_model(), pk = target_user_pk)
    prospect = get_object_or_404(Prospect, uid = prospect_uid)
    if user == request.user:
        messages.error(request, f"You can't remove yourself.")
        return redirect(reverse("tracker-detail", kwargs={"pk": prospect.pk}))
    if request.user.is_staff or (request.user in prospect.users.all()):
        prospect.users.remove(user)
        messages.error(request, f"Removed user's access.")
    return redirect(reverse("tracker-detail", kwargs={"pk": prospect.pk}))