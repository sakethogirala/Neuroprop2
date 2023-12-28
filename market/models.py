from django.db import models

class Lender(models.Model):
    title = models.CharField(max_length = 255)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True,  editable=True)

    def __str__(self):
        return self.title
    
