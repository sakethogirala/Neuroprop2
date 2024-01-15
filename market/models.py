from django.db import models
from django.conf import settings
from . import *
import uuid
from prospect.models import Prospect
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

    
class Note(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = "notes")
    file = models.FileField(upload_to="notes/", null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    lender = models.ForeignKey(Lender, on_delete=models.CASCADE, related_name = "notes")
    is_private = models.BooleanField(default = True)
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

    def __str__(self):
        return self.name
    
    def get_status_class(self):
        if self.status == "planned":
            return "secondary"
        if self.status == "in_progress":
            return "info"
        if self.status == "completed":
            return "success"