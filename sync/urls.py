from django.urls import path, include
from .views import *

urlpatterns = [
    path("email-webhook/", email_webhook, name="email_webhook"),
    path("lenders/", lender_syncs, name="lender_syncs")
]
