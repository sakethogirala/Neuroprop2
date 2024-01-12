from django.db import models
from django.conf import settings

class Lender(models.Model):
    title = models.CharField(max_length = 255)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True,  editable=True)

    def __str__(self):
        return self.title
    
class Note(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = "notes")
    file = models.FileField(upload_to="notes/", null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    lender = models.ForeignKey(Lender, on_delete=models.CASCADE, related_name = "notes")
    is_private = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add=True,  editable=True)

    def __str__(self) -> str:
        return f"{self.created_at} for {self.lender.title}"