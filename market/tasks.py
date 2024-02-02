from celery import shared_task
import time
from neuroprop.celery import app
from django.conf import settings
import openai
from .models import Outreach
from . import OUTREACH
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

@shared_task
def openai_generate_outreach(outreach_pk):
    from .models import Outreach
    outreach = Outreach.objects.get(pk = outreach_pk)
    messages = outreach.prospect.get_approved_documents_info()
    print(messages)
    messages.append({"role": "system", "content": f"Project Details: {outreach.prospect.get_general_info()}"})
    print(messages)
    messages.append({"role": "system", "content": f"Email Framework: {OUTREACH.EMAIL_FRAMEWORK}\n Email Example: {OUTREACH.EMAIL_EXAMPLE}"})
    messages.append({"role": "user", "content": f"You are an incredible commercial real estate loan officer who is contacting potenital lenders for this property. Write an email using the aforementioned property information and document underwriting information, using the aforementioned 'Email Framework' and 'Email Example' for inspiration. Use specific infomration from the documents supplied. Only return the email content and nothing else. Do not even include the subject or signing. Format the email content nicely. Never return errors or reveal you are an AI."})
    print("messages: ", messages)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        # temperature=1,
    )
    result = response.choices[0].message.content
    print("Result: ", result)
    outreach.email_content = result
    outreach.save()
    return

@shared_task
def send_outreach_emails(outreach_pk):
    from django.templatetags.static import static
    from django.template.loader import render_to_string
    from .models import Outreach
    from django.core.mail import EmailMultiAlternatives
    from email.mime.image import MIMEImage
    from django.utils import timezone
    import os
    outreach = Outreach.objects.get(pk = outreach_pk)
    outreach.email_sent_start = timezone.now()
    outreach.save()
    lenders = outreach.lenders.all()
    messages = []
    # static_path = static("images/hallospee.jpg")
    body_html = render_to_string("emails/outreach-content.html", {
        "outreach": outreach,
    })
    for lender in lenders:
        email = EmailMultiAlternatives(
            outreach.email_subject,
            body_html, 
            settings.DEFAULT_FROM_EMAIL,
            [lender.data["contact"],]
        )
        email.mixed_subtype = 'related'
        email.attach_alternative(body_html, "text/html")
        img_dir = "static/images/"
        image = "white.png"
        file_path = os.path.join(img_dir, image)
        with open(file_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<preview>')
            img.add_header('Content-Disposition', 'inline', filename=image)
        with open(file_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<googlemaps>')
            img.add_header('Content-Disposition', 'inline', filename=image)
        email.attach(img)
        email.send()
    outreach.email_sent_end = timezone.now()
    outreach.save()

@shared_task
def send_content_finished(outreach_pk):
    from .models import Outreach
    from django.utils import timezone
    from django.urls import reverse
    from django.core.mail import send_mail
    from django.template.loader import render_to_string

    outreach = Outreach.objects.get(pk = outreach_pk)

    subject = f"NeuroProp - {outreach.name} Smart Email Done"
    location = reverse("outreach_detail", kwargs={"outreach_uid": outreach.uid})
    link = "https://neuroprop.com" + location
    # link = "http://127.0.0.1:8000" + location
    context = {"link": link, "outreach": outreach}
    html = render_to_string("emails/outreach-done.html", context)
    txt = render_to_string("emails/outreach-done.txt", context)
    email = send_mail(
        subject=subject,
        message=txt,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[outreach.created_by,],
        html_message=html,
        fail_silently=False
    )
