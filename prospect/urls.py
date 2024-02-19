from django.urls import path, include
from .views import *

urlpatterns = [
    path("api-preds/", api_preds, name="api_preds"),
    path("custom-data-preds/", custom_data_preds, name="custom_data_preds"),
    path("custom-data-preds/<data_upload_pk>/", custom_data_preds_detail, name="custom_data_preds_detail"),
    path("upload/custom-data/", upload_custom_preds_data, name="upload_custom_preds_data"),
    path("refresh-data/", refresh_data, name="refresh_data")
]
