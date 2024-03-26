from django.urls import path

from .views import *

urlpatterns = [
    path("", tracker_main, name="tracker-main"),
    path("detail/<prospect_pk>/<document_type_pk>/", tracker_detail, name="tracker-detail"),
    path("detail/<prospect_pk>/", tracker_detail, name="tracker-detail"),
    path("upload-document", upload_document, name="upload-document"),
    path("delete-document/<document_uid>/", delete_document, name="delete-document"),
    path("download-document/", download_document, name="download-document"),
    path("document-override/<document_uid>/", override_document_check, name="override-document-check"),
    path("send-to-user/", send_to_user, name="send-to-user"),
    path("remove-user/", remove_user, name="remove-user"),
    path("ai/get-file-status/", poll_openai_document_check, name="poll_openai_document_check"),
    path("create-prospect/", create_prospect, name="create_prospect"),
    path("delete-prospect/<prospect_uid>/", delete_prospect, name="delete_prospect"),
    path("send-client-feedback/>/", send_client_feedback, name="send_client_feedback"),
    path("update-document-type-status", update_document_type_status, name="update_document_type_status"),
    path("ask-document-question/", ask_document_question, name="ask_document_question"),
    path("prospect/<prospect_pk>/edit/", edit_propsect, name="edit_propsect"),
    path("client/onboard/<prospect_uid>/", onboard_client, name="onboard_client"),
    path("smart/sort/<prospect_pk>/", smart_sort, name="smart-sort")
]