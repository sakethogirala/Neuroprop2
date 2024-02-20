from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import openai_sync_lender
from .models import LenderSync

@csrf_exempt
def email_webhook(request):
    if request.method == "POST":
        data = request.POST
        secret = data.get("secret")
        if secret == "testing123":
            body = data.get("body")
            subject = data.get("subject")
            from_email = data.get("from_email")
            from_name = data.get("from_name")
            lender_sync = LenderSync(
                data = {
                    "body": body,
                    "subject": subject,
                    "from_email": from_email,
                    "from_name": from_name
                }
            )
            openai_sync_lender.delay(lender_sync.pk)
            return HttpResponse("Hello World")
        return HttpResponse("Secret failed")