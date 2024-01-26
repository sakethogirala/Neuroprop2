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

@shared_task(bind=True)  # Use bind=True to bind the task instance to 'self'
def get_openai_document_feedback_status(self, document_pk):
    from .models import Document
    from django.utils import timezone
    document = Document.objects.get(pk=document_pk)
    feedback = document.openai_get_result(client, document.openai_document_feedback_thread_id, document.openai_document_feedback_run_id)
    print(feedback)
    
    if feedback:
        document.smart_checked = True
        document.openai_feedback_time = timezone.now()
        document.feedback = feedback["feedback"]
        document_correct = feedback["correct"]
        if document_correct:
            document.status = "pending"
            document.client_feedback = "Document type approved. Waiting for approval."
        else:
            document.status = "rejected"
            document.client_feedback = feedback["feedback"]
            send_rejected_upload.delay(document_pk)
            document.notify_document_rejected()

        document.save()
        document.document_type.staff_notifications = True
        document.document_type.save()
    else:
        try:
            # Retry the task
            self.retry(countdown=20, max_retries=10)
        except MaxRetriesExceededError:
            print("max tried")
            # Handle the situation after max retries are exceeded
            handle_max_retries_exceeded(document_pk)

def handle_max_retries_exceeded(document_pk):
    from .models import Document
    from django.utils import timezone
    document = Document.objects.get(pk=document_pk)
    document.smart_checked = True
    document.status = "pending"
    document.feedback = "AI was not able to analyze the file."
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