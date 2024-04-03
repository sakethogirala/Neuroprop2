from celery import shared_task
import time
from neuroprop.celery import app
from django.conf import settings
import openai

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

@shared_task
def start_openai_document_feedback(document_pk):
    from .models import Document
    document = Document.objects.get(pk = document_pk)
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Analyze this document attatched. No matter what open the file with ID {document.openai_file_id} and get it's content with whatever it takes and using any methods. Target Type is {document.document_type.general_name} with description {document.document_type.description}.",
        file_ids=[document.openai_file_id,]
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=settings.OPENAI_DOC_FEEDBACK_ID,
    )
    document.openai_document_feedback_run_id = run.id
    document.openai_document_feedback_thread_id = run.thread_id
    document.save()
    get_openai_document_feedback_status.delay(document_pk)


from celery.exceptions import MaxRetriesExceededError

# @shared_task(bind=True)  # Use bind=True to bind the task instance to 'self'
# def get_openai_document_feedback_status(self, document_pk):
#     from .models import Document
#     from django.utils import timezone
#     try:
#         document = Document.objects.get(pk=document_pk)
#         feedback = document.openai_get_result(client, document.openai_document_feedback_thread_id, document.openai_document_feedback_run_id)
#         print(feedback)
#         if feedback and 'correct' in feedback and 'feedback' in feedback:
#             document.smart_checked = True
#             document.openai_feedback_time = timezone.now()
#             document.feedback = feedback["feedback"]
#             document_correct = feedback["correct"]
#             if document_correct:
#                 document.status = "pending"
#                 document.client_feedback = "Document type approved. Waiting for approval."
#             else:
#                 document.status = "rejected"
#                 document.client_feedback = feedback["feedback"]
#                 # send_rejected_upload.delay(document_pk)
#                 document.notify_document_rejected()

#             document.save()
#             document.document_type.staff_notifications = True
#             document.document_type.save()
#         else:
#             try:
#                 # Retry the task
#                 self.retry(countdown=20, max_retries=10)
#             except MaxRetriesExceededError:
#                 print("max tried")
#                 # Handle the situation after max retries are exceeded
#                 document.smart_checked = True
#                 document.status = "pending"
#                 document.feedback = "AI was not able to analyze the file."
#                 document.save()
#     except Exception as e:
#         print("error: ", e)
#         # Handle the situation after max retries are exceeded
#         document.smart_checked = True
#         document.status = "pending"
#         document.feedback = "AI is analyzing file. Please wait..."
#         document.save() 


@shared_task(bind=True)
def get_openai_document_feedback_status(self, document_pk):
    from .models import Document
    from django.utils import timezone

    try:
        document = Document.objects.get(pk=document_pk)
        feedback = document.openai_get_result(client, document.openai_document_feedback_thread_id, document.openai_document_feedback_run_id)
        print(feedback)

        if not feedback:
            print("Result not ready, scheduling retry...")
            self.retry(countdown=20, max_retries=10)
        elif 'correct' in feedback and 'feedback' in feedback:
            # Process valid feedback
            document.smart_checked = True
            document.openai_feedback_time = timezone.now()
            document.feedback = feedback["feedback"]
            document_correct = feedback["correct"]

            document.status = "pending" if document_correct else "rejected"
            document.client_feedback = "Document type approved. Waiting for approval." if document_correct else feedback["feedback"]
            document.notify_document_rejected() if not document_correct else None
            document.save()
            document.document_type.staff_notifications = True
            document.document_type.save()
        else:
            # Handle invalid format or true error in data
            message = "Feedback format invalid or missing expected keys."
            # Common handler for scenarios where feedback is invalid or an error occurs
            document.smart_checked = True
            document.status = "pending"
            document.feedback = message
            document.save()

    except MaxRetriesExceededError:
        # Handle invalid format or true error in data
        message = "Document could not be analyzed. Max Retries Attempted."
        document.client_feedback = "Document could not be analyzed. Waiting for approval."
        document.smart_checked = True
        document.status = "pending"
        document.feedback = message
        document.save()

    except Exception as e:
        print(f"An error occurred: {e}")
        message = f"Document could not be analyzed. Error: {e}."
        document.client_feedback = "Document could not be analyzed. Waiting for approval."
        document.smart_checked = True
        document.status = "pending"
        document.feedback = message
        document.save()

@shared_task
def send_rejected_upload(document_pk):
    from .models import Document
    from django.utils import timezone
    from django.urls import reverse
    from django.core.mail import send_mail
    from django.template.loader import render_to_string

    document = Document.objects.get(pk = document_pk)

    subject = f"NeuroProp - {document.name} Rejected"
    location = reverse("tracker-detail", kwargs={"prospect_pk": document.document_type.prospect.pk, "document_type_pk": document.document_type.pk})
    link = "https://neuroprop.com" + location
    # link = "http://127.0.0.1:8000" + location
    context = {"link": link, "document": document}
    html = render_to_string("emails/document-rejected.html", context)
    txt = render_to_string("emails/document-rejected.txt", context)
    recipient_list = [user.email for user in document.document_type.prospect.users.filter(account_type="user")]
    if recipient_list:
        email = send_mail(
            subject=subject,
            message=txt,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html,
            fail_silently=False
        )



@shared_task
def start_openai_document_sort(document_pk, prospect_pk):
    from .models import Document
    from prospect.models import Prospect
    document = Document.objects.get(pk = document_pk)
    prospect = Prospect.objects.get(pk = prospect_pk)
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Sort this document attatched. No matter what open the file with ID {document.openai_file_id} and get it's content with whatever it takes and using any methods. The possible document types are {prospect.get_document_types_sorting()}",
        file_ids=[document.openai_file_id,]
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=settings.OPENAI_DOC_FEEDBACK_ID,
    )
    document.openai_document_sort_run_id = run.id
    document.openai_document_sort_thread_id = run.thread_id
    document.save()
    get_openai_document_sort_status.delay(document_pk, prospect_pk)


from celery.exceptions import MaxRetriesExceededError

@shared_task(bind=True)
def get_openai_document_sort_status(self, document_pk, prospect_pk):
    from .models import Document, DocumentType
    from django.utils import timezone
    document = Document.objects.get(pk=document_pk)
    result = document.openai_get_result(client, document.openai_document_sort_thread_id, document.openai_document_sort_run_id)
    print(result)
    try:
        if result:
            document.document_sorted_time = timezone.now()
            document_type = DocumentType.objects.filter(prospect__pk = prospect_pk, general_name = result["sort_result"])
            if document_type.exists():
                document.document_type = document_type.first()
                print("worked")
                print(document.document_type)
            document.save()
            document.document_type.staff_notifications = True
        else:
            try:
                self.retry(countdown=10, max_retries=10)
            except MaxRetriesExceededError:
                print("max tried")
                document.status = "pending"
                document.feedback = "Not."
                document.save()
    except Exception as e:
        print("error: ", e)
        # Handle the situation after max retries are exceeded
        document.save() 