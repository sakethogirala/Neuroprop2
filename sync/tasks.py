from celery import shared_task
from neuroprop.celery import app
from django.conf import settings
import openai
from . import SYNC
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

@shared_task
def openai_sync_lender(lender_sync_pk):
    from .models import LenderSync
    from market.models import Lender, Note
    import json
    from django.core.exceptions import ObjectDoesNotExist
    sync = LenderSync.objects.get(pk = lender_sync_pk)
    print(sync)
    messages = [
        {"role": "system", "content": "The following is an email content. Analyze if it is relevant for updating lender information in a commercial real estate lender database. Look for updates on loan terms, contact information, property types covered, states of operation, or any new services offered. Provide a concise note on the content that includes any found updates. Respond with a structured format: {'is_relevant': true, 'note': 'Found updates: [details of updates]'} for relevant and {'is_relevant': false, 'note': ''} for not relevant."},
        {"role": "user", "content": f"Subject: {sync.data['subject']}\n\nFrom: {sync.data['from_name']}\n\n{sync.data['body']}"},
    ]
    print("messages: ", messages)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        response_format={"type": "json_object"}
    )
    print(result)
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