from django.db import models
import uuid
from . import PROSPECT
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from urllib.parse import quote_plus

class DataUpload(models.Model):
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="data_uploads", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="data-uploads/", null=True, blank=True)
    analyze_start_time = models.DateTimeField(null=True, blank=True)
    analyze_end_time = models.DateTimeField(null=True, blank=True)

    def get_prospects_size(self):
        return self.dataUploads.all().count()
class ProspectData(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,  editable=True, null=False)
    data = models.JSONField(null=True)
    upload = models.ForeignKey(DataUpload, null=True, blank=True, related_name="dataUploads", on_delete=models.CASCADE)

class Address(models.Model):
    address = models.CharField(max_length=256, blank=True)
    address2 = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country   = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return str(self.address)

    def get_address(self):
        return render_to_string("includes/address.html", {"address": self})

    def get_geocode_address(self):
        components = [self.address, self.address2, self.city, self.state, self.postal_code, self.country]
        print("components: ", components)
        address_string = ', '.join(filter(None, components))  # Exclude None or empty components
        return quote_plus(address_string)

class Prospect(models.Model):
    uid = models.UUIDField(default=uuid.uuid4)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="prospects_owned", null=True, blank=True)
    contact = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True ,blank=True)
    name = models.CharField(max_length=200)
    status = models.CharField(choices=PROSPECT.STATUS_CHOICES, max_length=100, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null = True, blank = True)
    purpose = models.CharField(choices=PROSPECT.PURPOSE_CHOICES, max_length=100)
    property_type = models.CharField(choices=PROSPECT.PROPERTY_TYPE_CHOICES)
    users = models.ManyToManyField(get_user_model(), related_name="prospects")
    amount = models.DecimalField(default=0.00, max_digits=20, decimal_places=2, null=True, blank=True)
    context = models.TextField(null = True, blank = True)

    client_onboarded = models.BooleanField(default = False)
    client_scenario = models.JSONField(null = True, blank = True)


    def __str__(self) -> str:
        return self.name

    def get_progress_percentage(self):
        filtered_choices = [choice for choice in PROSPECT.STATUS_CHOICES if choice[0] != "failed"]
        for index, (key, _) in enumerate(filtered_choices):
            if key == self.status:
                return (index / (len(filtered_choices) - 1)) * 100

    def get_progress_class(self):
        if self.status == "pending":
            return "secondary"
        if self.status == "draft":
            return "secondary"
        if self.status == "in-progress":
            return "info"
        if self.status == "correcting":
            return "warning"
        if self.status == "completed":
            return "success"
        if self.status == "failed":
            return "danger"
        
    def get_document_progress_percentage(self):
        documents = self.document_types.all()
        if documents:
            return (documents.filter(status = "approved").count() / documents.count()) * 100
        return "0"
    
    def get_todo_count(self):
        documents = self.document_types.all()
        return documents.count() - documents.filter(status = "approved").count()
    
    def get_tofix_count(self):
        total = 0
        for doc in self.document_types.all():
            total += doc.get_tofix_count()
        return total
    
    def get_tasks_count(self):
        total = 0
        for doc in self.document_types.all():
            total += doc.get_review_count()
        return total
    
    def get_next_document_type(self):
        document_type = self.document_types.all().first()
        print(document_type.pk)
        return document_type.pk
    
    def are_staff_notifications(self):
        if self.document_types.filter(staff_notifications=True).exists():
            return True
        return False
    
    def are_client_notifications(self):
        if self.document_types.filter(client_notifications=True).exists():
            return True
        return False
    
    def get_approved_documents(self):
        list = []
        for doc_type in self.document_types.all():
            for doc in doc_type.documents.filter(status = "approved"):
                list.append(doc.openai_file_id)
        return list
    
    def get_approved_documents_info(self):
        messages = []
        for doc_type in self.document_types.filter(status = "pending"):
            for doc in doc_type.documents.filter(status = "approved"):
                messages.append({"role": "system", "content": f"Document {doc.name} underwriting information: {doc.feedback}"})
        for doc_type in self.document_types.filter(status = "approved"):
            for doc in doc_type.documents.exclude(status = "rejected"):
                messages.append({"role": "system", "content": f"Document {doc.name} underwriting information: {doc.feedback}"})
        return messages
    
    def get_general_info(self):
        return f"{self.get_property_type_display()} {self.get_purpose_display()} for ${self.amount} located at {self.address.get_address()}. Circumstances and context: {self.context} and {self.client_scenario}"
    
    def get_document_types_series(self):
        return [self.document_types.filter(status="approved").count(), self.document_types.filter(status="pending").count(), self.document_types.filter(status="not_uploaded").count(), self.document_types.filter(status="rejected").count()]

    def get_document_progress(self):
        approved = self.document_types.filter(status="approved").count()
        return f"{approved} / {self.document_types.all().count()}"

    def get_document_types_sorting(self):
        string = ""
        for doc_type in self.document_types.all():
            string += f"{doc_type.general_name}, "
        return string

def get_image_path(instance, filename):
    return f"documents/{instance.prospect.uid}/{filename}"

class Photo(models.Model):
    uid = models.UUIDField(default=uuid.uuid4)
    prospect = models.ForeignKey(Prospect, related_name = "photos", on_delete = models.CASCADE)
    image = models.ImageField(upload_to=get_image_path)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="uploaded_photos")
    created_at = models.DateTimeField(auto_now_add=True)