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
    messages.append({"role": "user", "content": f"You are an incredible commercial real estate loan officer who is contacting potenital lenders for this property. Write an email using the aforementioned property information and document underwriting information, using the aforementioned 'Email Framework' and 'Email Example' for inspiration. Use specific infomration from the documents supplied. Only return the email content and nothing else. Do not even include the subject or signing or intro. Format the email content nicely. Never return errors or reveal you are an AI. Always have real values placed and don't use any placeholders."})
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
    from django.conf import settings
    import requests
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from email.mime.image import MIMEImage
    from .models import Outreach
    from django.utils import timezone

    outreach = Outreach.objects.get(pk=outreach_pk)
    outreach.email_sent_start = timezone.now()
    outreach.save()
    lenders = outreach.lenders.all()

    for lender in lenders:
        body_html = render_to_string("emails/outreach-content.html", {
            "lender": lender,
            "outreach": outreach,
            "preview": False
        })

        # Generate the Google Maps image URL
        google_maps_image_url = f"https://maps.googleapis.com/maps/api/staticmap?center={outreach.prospect.address.get_geocode_address()}&zoom=15&markers=color:red%7C{outreach.prospect.address.get_geocode_address()}&size=500x300&maptype=roadmap&key={settings.GOOGLE_MAPS_API_KEY}"
        
        # Download the Google Maps image
        response = requests.get(google_maps_image_url)
        map_image_data = response.content

        email = EmailMultiAlternatives(
            subject=outreach.email_subject,
            body=body_html,  # This is the text body, not used here but required
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[lender.data["contact_email"]]
        )
        email.mixed_subtype = 'related'
        email.attach_alternative(body_html, "text/html")

        # Attach the outreach image if available
        file_path = outreach.email_image.file.path
        with open(file_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<preview>')
            img.add_header('Content-Disposition', 'inline', filename=outreach.email_image.name)
            email.attach(img)

        # Attach the Google Maps image
        map_img = MIMEImage(map_image_data)
        map_img.add_header('Content-ID', '<googlemaps>')
        map_img.add_header('Content-Disposition', 'inline')
        email.attach(map_img)

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
