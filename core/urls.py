from django.urls import path, include
from .views import *

urlpatterns = [
    path("lender-map/", lender_map, name="lender-map"),
    path("", index, name="index")
]
