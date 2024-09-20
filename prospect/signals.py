from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Prospect
from . import PROSPECT
from tracker import DOCUMENT
from tracker.models import DocumentType

def create_files(instance, docs):
    for doc in docs:
        DocumentType.objects.get_or_create(
            prospect=instance,
            type=doc[0],
            defaults={
                'general_name': doc[1],
                'description': doc[2]
            }
        )

def create_image_file(instance):
    DocumentType.objects.get_or_create(
        prospect=instance,
        type="Property Images",
        defaults={
            'general_name': "PropertyImage",
            'description': "Images of properties",
            'is_image': True
        }
    )

@receiver(post_save, sender=Prospect)
def post_save_prospect(sender, instance, created, *args, **kwargs):
    if created:
        create_image_file(instance)
        if instance.property_type == "hotel":
            create_files(instance, DOCUMENT.HOTEL_DOCS)
        elif instance.property_type == "self-storage":
            create_files(instance, DOCUMENT.SELF_STORAGE_DOCS)
        elif instance.property_type == "multifamily":
            create_files(instance, DOCUMENT.MULTI_FAMILY_DOCS)
        
        # Add SREO Document Type only once
        create_files(instance, [("SREO Document", "SREODocument", "Specialized Real Estate Operating Document")])