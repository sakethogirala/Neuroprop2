from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from tracker.models import Document
from market.models import Lender
from django.utils import timezone
from prospect.models import Prospect
from market.models import Outreach
from datetime import timedelta

@login_required
def index(request):
    if not request.user.staff_access():
        return redirect("tracker-main")
    
    current_month = timezone.now().month
    today = timezone.now().date()

    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    properties = request.user.prospects.filter(users=request.user)
    properties_added_this_month = properties.filter(created_at__month=current_month).count()
    documents = Document.objects.filter(document_type__prospect__users=request.user)
    events = list(documents)
    lenders_added_this_month = Lender.objects.filter(created_at__month=current_month).count()
    lender_count = Lender.objects.all().count()
    task_count = sum(property.get_todo_count() for property in Prospect.objects.filter(status="in-progress"))
    tasks = Document.objects.filter(document_type__prospect__users=request.user, status="pending")
    tasks_this_week = tasks.filter(openai_feedback_time__range=[start_of_week, end_of_week]).count()
    outreaches = Outreach.objects.filter(created_by=request.user)
    outreaches_added_this_month = outreaches.filter(created_at__month=current_month).count()
    context = {
        'lenders_added_this_month': lenders_added_this_month,
        "lender_count": lender_count,
        "events": events,
        "properties": properties,
        "properties_added_this_month": properties_added_this_month,
        "tasks": tasks,
        "task_count": task_count,
        "tasks_this_week": tasks_this_week,
        "outreaches": outreaches,
        "outreaches_added_this_month": outreaches_added_this_month,
    }
    return render(request, "index.html", context)