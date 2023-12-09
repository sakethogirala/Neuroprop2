from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def lender_map(request):
    context = {

    }
    return render(request, "lender-map.html", context)

@login_required
def index(request):
    return render(request, "index.html")