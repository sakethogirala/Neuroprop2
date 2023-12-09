from django.db.models.signals import pre_save
from django.dispatch import receiver
from account.models import User
from account.utils import *

@receiver(pre_save, sender=User)
def pre_save_user(sender, instance, *args, **kwargs):
    if not instance.activation_key:
        instance.activation_key = generate_activation_code(instance)