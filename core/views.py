from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    properties = request.user.prospects.all()
    context = {
        "properties": properties
    }
    return render(request, "index.html", context)