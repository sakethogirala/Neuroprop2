from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Document

# @receiver(pre_save, sender=Document)
# def pre_save_document(sender, instance, *args, **kwargs):
#     if instance.status == "rejected":
#         print("sending rejection email...")
#         instance.notify_document_rejected()