from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error
from .forms import SignUpForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib import messages
from . import ACCOUNT
from django.contrib.auth import update_session_auth_hash

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect("login")
    else:
        form = SignUpForm()
    
    context = {
        "form": form,
        'timezones': ACCOUNT.common_timezones
    }
    return render(request, "registration/signup.html", context)
    
def activate_account(request, token):
    user = get_object_or_404(get_user_model(), activation_key = token)
    user.is_active = True
    user.save()
    login(request, user)
    messages.success(request, "Neuroprop Account Activated!")
    return redirect("index")

def resend_activation(request):
    email = request.POST.get("email")
    user = get_user_model().objects.filter(email=email).first()
    if request.method == "POST":
        if user:
            if user.is_active:
                messages.error(request, "{} is already activated.".format(user.email))
            else:
                activation_email = user.send_confirmation_email(request)
                messages.success(request, f"Check {email} to activate your account.")
        else:
            messages.error(request, "There is no account with that email.")
    return render(request, "registration/activate.html")

def settings(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST.get('timezone')
        # print(request.session['django_timezone'])
    
    context = {
        'timezones': ACCOUNT.common_timezones
    }
    return render(request, "account/settings.html", context)

def user_set_password(request, token):
    user = get_object_or_404(get_user_model(), activation_key = token)
    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Important!
            user.is_allowed = True
            user.save()
            login(request, user)
            print(user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect("index")
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        login(request, user)
        form = SetPasswordForm(user)
    context = {
        "form": form,
    }
    return render(request, "registration/user-set-password.html", context)

# Profile view
@login_required
def profile(request):
    return render(request, "account/profile.html")

# Support view
from django.core.mail import send_mail
from django.conf import settings

@login_required
def support_view(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        user_email = request.user.email
        
        # Send email to support
        send_mail(
            f"Support Request: {subject}",
            f"From: {user_email}\n\n{message}",
            settings.DEFAULT_FROM_EMAIL,
            [settings.SUPPORT_EMAIL],
            fail_silently=False,
        )
        
        messages.success(request, "Your support request has been sent. We'll get back to you soon.")
        return redirect('support')
    
    return render(request, 'account/support.html')


# Add these new views

@login_required
def lock_screen(request):
    request.session['is_locked'] = True
    return render(request, 'account/lock_screen.html')

@login_required
def unlock_screen(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.email, password=password)
        if user is not None:
            login(request, user)
            request.session['is_locked'] = False
            messages.success(request, "Screen unlocked successfully!")
            return redirect('index')
        else:
            messages.error(request, "Invalid password. Please try again.")
    return render(request, 'account/lock_screen.html')