from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import openai_sync_lender
from .models import LenderSync
from .models import LenderSync
from market.models import Lender, Note
import json
from django.core.exceptions import ObjectDoesNotExist
import openai
from django.conf import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

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
            sync = LenderSync.objects.create(
                data = {
                    "body": body,
                    "subject": subject,
                    "from_email": from_email,
                    "from_name": from_name
                }
            )

            messages = [
                {"role": "system", "content": "The following is an email content. Analyze if it is relevant for updating lender information in a commercial real estate lender database. Look for updates on loan terms, contact information, property types covered, states of operation, or any new services offered. Provide a concise note on the content that includes any found updates. Respond with a structured json format: {'is_relevant': true, 'note': 'Found updates: [details of updates]'} for relevant and {'is_relevant': false, 'note': ''} for not relevant."},
                {"role": "user", "content": f"Subject: {sync.data['subject']}\n\nFrom: {sync.data['from_name']}\n\n{sync.data['body']}"},
            ]
            print("messages: ", messages)
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=messages,
                response_format={"type": "json_object"}
            )
            print(response)
            result = response.choices[0].message.content
            print(result)
            try:
                result_data = json.loads(result)
                is_relevant = result_data.get('is_relevant', False)
                if is_relevant:
                    from_email = sync.data["from_email"]
                    try:
                        lender = Lender.objects.get(data__contact_email=from_email)
                        print(f"Match found: {lender.name}")
                        sync.status = "matched"
                        note = Note.objects.create(
                            text = result_data.get("note"),
                            lender = lender,
                            is_smart = True
                        )
                        sync.note = note

                    except ObjectDoesNotExist:
                        print("No matching lender found.")
                        sync.status = "unmatched"
                else:
                    sync.status = "not_relevant"
                sync.save()
            except json.JSONDecodeError:
                print("Failed to parse the model's response as JSON.")
            return HttpResponse("Hello World")
        return HttpResponse("Secret failed")
    

def lender_syncs(request):
    lender_syncs = LenderSync.objects.all()

    context = {
        "syncs": lender_syncs
    }
    return render(request, "sync/lender_syncs.html", context)