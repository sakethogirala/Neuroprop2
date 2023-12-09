from django.urls import path, include
from .views import *

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("", include('django.contrib.auth.urls')),
    path("activate/<token>/", activate_account, name="activate_account"),
    path("resend/activation/", resend_activation, name="resend_activation"),
    path("set-password/<token>/", user_set_password, name="set_password")
]
