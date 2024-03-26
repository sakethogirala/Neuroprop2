from django.db import models
import uuid
from .utils import get_doc_path
from . import DOCUMENT, DOCUMENT_TYPE
from prospect.models import Prospect
from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from .manager import DocumentTypeManager
import json
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail

class DocumentType(models.Model):
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE, related_name="document_types")
    type = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, null=True, blank=True)
    general_name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, choices=DOCUMENT_TYPE.STATUS_CHOICES, default="not_uploaded")
    created_at = models.DateTimeField(auto_now_add=True)
    objects = DocumentTypeManager()
    document_count = models.IntegerField(default=1)
    staff_notifications = models.BooleanField(default = False)
    client_notifications = models.BooleanField(default = False)
    is_image = models.BooleanField(default = False)

    def __str__(self) -> str:
        return f"{self.prospect} - {self.type}"

    def get_status_class(self):
        if self.status == "not_uploaded":
            return "secondary"
        if self.status == "pending":
            return "warning"
        if self.status == "rejected":
            return "danger"
        if self.status == "approved":
            return "success"
    
    def get_tofix_count(self):
        return len(self.documents.filter(status="rejected"))

    def get_review_count(self):
        return len(self.documents.filter(status="pending"))

class Document(models.Model):
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="uploaded_documents")
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, related_name="documents", null=True)
    uid = models.UUIDField(default=uuid.uuid4)
    file = models.FileField(upload_to=get_doc_path, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(max_length=1000, null=True, blank=True)
    client_feedback = models.TextField(max_length=1000, null=True, blank=True)
    client_question = models.TextField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=100, choices=DOCUMENT.STATUS_CHOICES, default="pending")
    overridden = models.BooleanField(default=False)
    smart_checked = models.BooleanField(default = False)

    openai_file_id = models.CharField(max_length=100, null=True, blank=True)
    openai_thread_id = models.CharField(max_length=100, null=True, blank=True)
    
    openai_document_feedback_thread_id = models.CharField(max_length=100, null=True, blank=True)
    openai_document_feedback_run_id = models.CharField(max_length=100, null=True, blank=True)
    openai_feedback_time = models.DateTimeField(null=True, blank=True)

    openai_document_sort_thread_id = models.CharField(max_length=100, null=True, blank=True)
    openai_document_sort_run_id = models.CharField(max_length=100, null=True, blank=True)
    document_sorted_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.document_type} - {self.status}"

    def file_checked(self):
        return self.smart_checked

    def get_status_class(self):
        if self.status == "not_uploaded":
            return "secondary"
        if self.status == "pending":
            return "warning"
        if self.status == "rejected":
            return "danger"
        if self.status == "approved":
            return "success"

    def get_icon_class(self):
        if self.status == "not_uploaded":
            return "secondary"
        if self.status == "pending":
            return "mdi mdi-exclamation-thick"
        if self.status == "rejected":
            return "uil uil-times"
        if self.status == "approved":
            return "uil uil-check"
 
    def openai_upload_file(self, client):
        file = client.files.create(
            file=self.file.read(),
            purpose = "assistants"
        )
        self.openai_file_id = file.id
        self.save()
        return file.id
            
    def openai_get_result(self, client, thread_id, run_id):
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            print(run.status)
            if run.status == "requires_action":
                print("REQUIRED ACTION \n")
                call_id = run.required_action.submit_tool_outputs.tool_calls[0].id
                output = json.loads(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
                print(output)
                return output
            if run.status == "completed":
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                for message in messages:
                    if message.content:  # Check if message.content is not empty
                        value = message.content[0].text.value
                        return value
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            # Optionally, return or handle the error in a more specific way
            return False


    def notify_document_rejected(self):
        subject = f"NeuroProp - {self.name} Rejected"
        location = reverse("tracker-detail", kwargs={"prospect_pk": self.document_type.prospect.pk, "document_type_pk": self.document_type.pk})
        link = "https://neuroprop.com" + location
        # link = "http://127.0.0.1:8000" + location
        context = {"link": link, "document": self}
        html = render_to_string("emails/document-rejected.html", context)
        txt = render_to_string("emails/document-rejected.txt", context)
        recipient_list = [user.email for user in self.document_type.prospect.users.filter(account_type="user")]
        if recipient_list:
            email = send_mail(
                subject=subject,
                message=txt,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html,
                fail_silently=False
            )