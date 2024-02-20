from django.db import models
from django.conf import settings
from . import *
import uuid
from prospect.models import Prospect
import json
from tracker.models import Document
class Lender(models.Model):
    title = models.CharField(max_length = 255)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True,  editable=True)

    def __str__(self):
        return self.title
    
    def display_property_types(self):
        # Assuming OUTREACH.PROPERTY_TYPES is a list of tuples
        mapping = dict(OUTREACH.PROPERTY_TYPES)

        # Extracting the property types from the data, with a default to an empty list
        prop_types = self.data.get("property_types", [])

        # Convert each property type code to its full name, or use the code itself if not found in mapping
        prop_type_names = [mapping.get(prop_type, prop_type) for prop_type in prop_types]

        # Join the names into a single string separated by commas
        return ", ".join(prop_type_names)

    def greeting(self):
        contact_name = self.data.get('contact_name', '').split()[0] if self.data.get('contact_name') else ''
        first_name = contact_name.split()[0] if contact_name else ''
        
        # Use the first name if available, otherwise fall back to the lender's title
        if first_name:
            return f"{first_name}"
        else:
            return f"{self.title}"
    
class Note(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = "notes", null=True, blank=True)
    file = models.FileField(upload_to="notes/", null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    lender = models.ForeignKey(Lender, on_delete=models.CASCADE, related_name = "notes")
    is_private = models.BooleanField(default = True)
    is_smart = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add=True,  editable=True)

    def __str__(self) -> str:
        return f"{self.created_at} for {self.lender.title}"

class Outreach(models.Model):
    uid = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=255, null=True, blank=True)
    lenders = models.ManyToManyField(Lender)
    prospect = models.ForeignKey(Prospect, null=True, blank=True, on_delete=models.SET_NULL, related_name="outreaches")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="outreaches")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=OUTREACH.STATUS_CHOICES, default="planned")
    description = models.TextField(blank=True, null=True)

    email_content = models.TextField(null=True, blank=True)
    email_subject = models.CharField(null=True, blank=True)
    email_image = models.ForeignKey(Document, null=True, blank=True, on_delete = models.SET_NULL)
    email_sent_start = models.DateTimeField(null=True, blank=True)
    email_sent_end = models.DateTimeField(null=True, blank=True)
    schedule_call_url = models.URLField(max_length=200, null=True, blank=True)

    openai_outreach_thread_id = models.CharField(max_length=100, null=True, blank=True)
    openai_outreach_run_id = models.CharField(max_length=100, null=True, blank=True)
    openai_outreach_time = models.DateTimeField(null=True, blank=True)
    openai_outreach_time_start = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name
    
    def get_status_class(self):
        if self.status == "planned":
            return "secondary"
        if self.status == "in_progress":
            return "info"
        if self.status == "completed":
            return "success"

    def openai_get_result(self, client, thread_id, run_id):
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
                value = message.content[0].text.value
                return value
        return False
    
    def get_image_document_type(self):
        return self.prospect.document_types.filter(is_image = True).first()

# # Example OpenAI Python library request
# MODEL = "gpt-3.5-turbo"
# response = client.chat.completions.create(
#     model=MODEL,
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Knock knock."},
#         {"role": "assistant", "content": "Who's there?"},
#         {"role": "user", "content": "Orange."},
#     ],
#     temperature=0,
# )
