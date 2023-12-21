from django.db import models
from django.db.models import Case, When, Value, IntegerField

class DocumentTypeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            priority=Case(
                When(status='not_uploaded', then=Value(1)),
                When(status='rejected', then=Value(2)),
                When(status='revising', then=Value(3)),
                When(status='pending', then=Value(4)),
                When(status='approved', then=Value(5)),
                default=Value(6),
                output_field=IntegerField()
            )
        ).order_by('priority')
