from django.db import models
from market.models import Lender, Note
from . import SYNC

class LenderSync(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    lender = models.ForeignKey(Lender, null = True, related_name="syncs", on_delete = models.SET_NULL, blank=True)
    note = models.ForeignKey(Note, null=True, related_name = "syncs", on_delete = models.SET_NULL, blank=True)
    data = models.JSONField(default=dict)
    status = models.CharField(choices=SYNC.LENDER_SYNC_CHOICES, max_length=100, default="unprocessed")

    def __str__(self) -> str:
        return f"{self.created_at}"
    
    def get_status_class(self):
        if self.status == "unprocessed":
            return "secondary"
        if self.status == "matched":
            return "success"
        if self.status == "unmatched":
            return "warning"
        if self.status == "not_relevant":
            return "secondary"