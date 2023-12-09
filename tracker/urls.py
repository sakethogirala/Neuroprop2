from django.urls import path

from .views import *

urlpatterns = [
    path("", TrackerMain.as_view(), name="tracker-main"),
    path("detail/<pk>/", TrackerDetail.as_view(), name="tracker-detail"),
    path("upload-document", upload_document, name="upload-document"),
    path("delete-document/", delete_document, name="delete-document"),
    path("download-document/", download_document, name="download-document"),
    path("send-to-user/", send_to_user, name="send-to-user"),
    path("remove-user/", remove_user, name="remove-user"),
    path("ai/get-status/", get_openai_status, name="get_ai_doc_status")
]