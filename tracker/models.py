from django.db import models
import uuid
from .utils import get_doc_path
from . import DOCUMENT
from prospect.models import Prospect
from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from .manager import DocumentTypeManager
class DocumentType(models.Model):
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE, related_name="document_types")
    type = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, null=True, blank=True)
    general_name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, choices=DOCUMENT.STATUS_CHOICES, default="not_uploaded")
    created_at = models.DateTimeField(auto_now_add=True)
    objects = DocumentTypeManager()
    document_count = models.IntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.prospect} - {self.type}"

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
    
    openai_thread_file_check_id = models.CharField(max_length=100, null=True, blank=True)
    openai_run_file_check_id = models.CharField(max_length=100, null=True, blank=True)
    file_checked = models.BooleanField(default = False)

    openai_file_id = models.CharField(max_length=100, null=True, blank=True)
    openai_assistant_id = models.CharField(max_length=100, null=True, blank=True)
    openai_thread_id = models.CharField(max_length=100, null=True, blank=True)
    openai_run_id = models.CharField(max_length=100, null=True, blank=True)
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
        # print("doing assistant file: ", self.openai_file_id)
        # assistant_file = client.beta.assistants.files.create(
        #     assistant_id=settings.OPENAI_ASSISTANT_ID, 
        #     file_id=self.openai_file_id
        # )
        # print("ASSISTANT FILE: ", assistant_file)
        return file.id

    def openai_check_file(self, client):
        print("starting openai feedback...")
        # upload file to OpenAI then use the file ID in message
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Analyze this document attatched to see if it's the correct type. No matter what open the file and get it's content with whatever it takes and using any methods. Target Type is {self.document_type.general_name} with description {self.document_type.description}",
            file_ids=[self.openai_file_id,]
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=settings.OPENAI_ASSISTANT_FILE_CHECK_ID,
        )
        print("SECOND: ", message)
        print(run)
        self.openai_run_file_check_id = run.id
        self.openai_thread_file_check_id = run.thread_id
        self.save()
        return
    
    def openai_get_file_check(self, client):
        print("checking ai file...")
        run = client.beta.threads.runs.retrieve(thread_id=self.openai_thread_file_check_id, run_id=self.openai_run_file_check_id)
        print(run)
        print(run.status)
        if run.status == "requires_action":
            print("REQUIRED ACTION \n")
            call_id = run.required_action.submit_tool_outputs.tool_calls[0].id
            new_run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.openai_thread_file_check_id,
            run_id=self.openai_run_file_check_id,
            tool_outputs=[
                {
                    "tool_call_id": call_id,
                    "output": "{success: 'true'}",
                },
                ]
            )
            print(new_run)
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=self.openai_thread_file_check_id)
            print("messages: ")
            print(messages)
            for message in messages:
                return message.content[0].text.value
        print("not done yet")
        return False

        
    def openai_start_feedback(self, client):
        print("starting openai feedback...")
        self.openai_ran_at = timezone.now()

        file_id = self.openai_upload_file(client)
        print("FILE ID: ", file_id)
        # upload file to OpenAI then use the file ID in message

        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Analyze this document attatched. No matter what open the file and get it's content with whatever it takes and using any methods. {self.description}",
            file_ids=[file_id,]
        )


        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=settings.OPENAI_ASSISTANT_UNDERWRITE_ID,
        )


        # run = client.beta.threads.create_and_run(
        #     assistant_id=settings.OPENAI_ASSISTANT_ID,
        #     thread={
        #         "messages": [{
        #             "role": "user",
        #             "content": f"Provide digestable succinct feedback on the uploaded document {file_id}. The purpose of this document is: {self.description}",
        #             "file_ids": [file_id]
        #         }]
        #         }
        #         )
        print(run)
        self.openai_run_id = run.id
        self.openai_thread_id = run.thread_id
        self.save()
        return

    def openai_get_feedback(self, client):
        print("getting ai feedback...")
        run = client.beta.threads.runs.retrieve(thread_id=self.openai_thread_id, run_id=self.openai_run_id)
        print(run)
        if run.status == "completed":
            print("done!")
            messages = client.beta.threads.messages.list(thread_id=self.openai_thread_id)
            print("messages: ")
            print(messages)
            for message in messages:
                return message.content[0].text.value
        print("not done yet")
        return False

