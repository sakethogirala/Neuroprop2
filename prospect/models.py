from django.db import models
import uuid
from . import PROSPECT
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

class Data(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,  editable=True, null=False)
    data = models.JSONField(null=True)

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

class Prospect(models.Model):
    uid = models.UUIDField(default=uuid.uuid4)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True ,blank=True)
    name = models.CharField(max_length=200)
    status = models.CharField(choices=PROSPECT.STATUS_CHOICES, max_length=100, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(choices=PROSPECT.PURPOSE_CHOICES, max_length=100)
    property_type = models.CharField(choices=PROSPECT.PROPERTY_TYPE_CHOICES)
    users = models.ManyToManyField(get_user_model(), related_name="prospects")
    amount = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    
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
    
    def get_next_document_type(self):
        document_type = self.document_types.all().first()
        print(document_type.pk)
        return document_type.pk