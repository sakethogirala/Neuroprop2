from django.urls import path, include
from .views import *
from .views import SREODataListView
from . import views

urlpatterns = [
    path("api-preds/", api_preds, name="api_preds"),
    path("custom-data-preds/", custom_data_preds, name="custom_data_preds"),
    path("custom-data-preds/<data_upload_pk>/", custom_data_preds_detail, name="custom_data_preds_detail"),
    path("upload/custom-data/", upload_custom_preds_data, name="upload_custom_preds_data"),
    path("refresh-data/", refresh_data, name="refresh_data"),
    path('sreo-data/', SREODataListView.as_view(), name='sreo_data_list'),
    path('get-similar-properties/', views.get_similar_properties, name='get_similar_properties'),
    path('similar-properties/<str:property_id>/', similar_properties, name='similar_properties'),
]
