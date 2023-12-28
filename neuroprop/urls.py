from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("account.urls")),
    path("tracker/", include("tracker.urls")),
    path("prospect/", include("prospect.urls")),
    path("market/", include("market.urls")),
]
