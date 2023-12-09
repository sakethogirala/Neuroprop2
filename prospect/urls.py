from django.urls import path, include
from .views import *

urlpatterns = [
    path("search/", get_preds, name="get_preds"),
    path("refresh-data/", refresh_data, name="refresh_data")
]
