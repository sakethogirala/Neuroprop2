from django.urls import path, include
from .views import *

urlpatterns = [
    path("lender-map/", lender_map, name="lender-map"),
    path("lenders/", lenders, name="lenders"),
    path("create-lender/", create_lender, name="create_lender")
]
