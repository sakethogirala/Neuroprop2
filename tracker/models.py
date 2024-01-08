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

    def __str__(self) -> str:
        return f"{self.prospect} - {self.type}"

    def get_status_class(self):
        if self.status == "not_uploaded":
            return "secondary"
        if self.status == "pending":
            return "info"
        if self.status == "approved":
            return "success"

class Document(models.Model):
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, related_name="documents", null=True)
    uid = models.UUIDField(default=uuid.uuid4)
    file = models.FileField(upload_to=get_doc_path, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=False)
    feedback = models.TextField(max_length=1000, null=True, blank=True)
    client_feedback = models.TextField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=100, choices=DOCUMENT.STATUS_CHOICES, default="pending")
    overridden = models.BooleanField(default=False)
    
    openai_check_thread_id = models.CharField(max_length=100, null=True, blank=True)
    openai_check_run_id = models.CharField(max_length=100, null=True, blank=True)
    file_checked = models.BooleanField(default = False)

    openai_file_id = models.CharField(max_length=100, null=True, blank=True)

    openai_feedback_thread_id = models.CharField(max_length=100, null=True, blank=True)
    openai_feedback_run_id = models.CharField(max_length=100, null=True, blank=True)
    openai_feedback_ran_at = models.DateTimeField(null=True, blank=True)

    openai_ran_at = models.DateTimeField(null=True, blank=True)


    def __str__(self) -> str:
        return f"{self.document_type} - {self.status}"

    def openai_upload_file(self, client):
        print("uploading file...")
        file = client.files.create(
            file=self.file.read(),
            purpose = "assistants"
        )
        print(file)
        self.openai_file_id = file.id
        self.save()
        return file.id

    def openai_check_start(self, client):
        print("starting openai file checker...")
        # upload file to OpenAI then use the file ID in message
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Analyze this document attatched. No matter what open the file and get it's content with whatever it takes and using any methods. Target Type is {self.document_type.general_name} with description {self.document_type.description}",
            file_ids=[self.openai_file_id,]
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=settings.OPENAI_ASSISTANT_MASTER_ID,
        )
        self.openai_check_run_id = run.id
        self.openai_check_thread_id = run.thread_id
        self.save()
        return
        
    def openai_feedback_start(self, client):
        print("starting openai document feedback...")
        # upload file to OpenAI then use the file ID in message
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Analyze this document attatched to provide feedback. No matter what open the file and get it's content with whatever it takes and using any methods. Target Type is {self.document_type.general_name} with description {self.document_type.description}",
            file_ids=[self.openai_file_id,]
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=settings.OPENAI_ASSISTANT_UNDERWRITE_ID,
        )
        self.openai_document_feedback_run_id = run.id
        self.openai_document_feedback_thread_id = run.thread_id
        self.save()
        return
    
    def openai_get_result(self, client, thread_id, run_id):
        print("checking ai file...")
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print(run)
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
                value = message.content[0].text.value
                return value
        print("not done yet")
        return False
