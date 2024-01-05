from django.urls import path

from .views import *

urlpatterns = [
    path("", TrackerMain.as_view(), name="tracker-main"),
    path("detail/<prospect_pk>/<document_type_pk>/", tracker_detail, name="tracker-detail"),
    path("upload-document", upload_document, name="upload-document"),
    path("delete-document/<document_uid>/", delete_document, name="delete-document"),
    path("download-document/", download_document, name="download-document"),
    path("document-override/<document_uid>/", override_document_check, name="override-document-check"),
    path("send-to-user/", send_to_user, name="send-to-user"),
    path("remove-user/", remove_user, name="remove-user"),
    path("ai/get-status/", get_openai_status, name="get_ai_doc_status"),
    path("ai/get-file-status/", get_openai_get_file_check, name="get_ai_file_check_status"),
    path("create-prospect/", create_prospect, name="create_prospect"),
    path("delete-prospect/<prospect_uid>/", delete_prospect, name="delete_prospect"),
    path("send-client-feedback/>/", send_client_feedback, name="send_client_feedback")
]