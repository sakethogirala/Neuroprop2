from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

def account_allowed(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.user.is_authenticated:
            token = request.user.activation_key
            if not request.user.is_allowed and request.path != f"/accounts/set-password/{token}/":
                print(request.path)
                messages.error(request, "Please set your password first!")
                return redirect(reverse("set_password", kwargs={"token": request.user.activation_key}))

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware