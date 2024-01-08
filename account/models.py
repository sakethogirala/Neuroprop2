from email.policy import default
import uuid
from django.urls import reverse
from django.template.loader import render_to_string
from account import ACCOUNT
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import CustomUserManager
from django.core.mail import send_mail
from django.conf import settings


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    account_type = models.CharField(max_length=100, choices=ACCOUNT.TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null = True, blank = True)
    date_joined = models.DateTimeField(default=timezone.now)
    activation_key  = models.CharField(max_length=50)

    is_allowed = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    def staff_access(self):
        return self.is_staff or self.account_type in ['staff', 'partner']

    def send_confirmation_email(self, request):
        if not self.is_active:
            location = reverse("activate_account", kwargs={"token": self.activation_key})
            link = request.build_absolute_uri(location)

            text_msg = render_to_string("registration/emails/email_confirmation.txt", {'user': self.name, 'link': link})
            email = send_mail(
                subject="Confirm Neuroprop Account",
                message=text_msg,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email,],
                fail_silently=False
            )
            return email

    def send_password_set_email(self, request):
        location = reverse("set_password", kwargs={"token": self.activation_key})
        link = request.build_absolute_uri(location)

        text_msg = render_to_string("registration/emails/set_password.txt", {'user': self.name, 'link': link})
        email = send_mail(
            subject="Configure NeuroProp Account",
            message=text_msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email,],
            fail_silently=False
        )
        return email