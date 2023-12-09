from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Prospect
from . import PROSPECT
from tracker import DOCUMENT
from tracker.models import Document

def create_files(instance, docs):
    for doc in docs:
        new_doc = Document.objects.create(
            prospect = instance
        )
        new_doc.name = doc[1]
        new_doc.type = doc[0]
        new_doc.description = doc[2]
        new_doc.save()

@receiver(post_save, sender=Prospect)
def pre_save_user(sender, instance, created, *args, **kwargs):
    if created:
        if instance.property_type == "hotel":
            create_files(instance, DOCUMENT.HOTEL_DOCS)
        if instance.property_type == "self-storage":
            create_files(instance, DOCUMENT.SELF_STORAGE_DOCS)
