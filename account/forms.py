from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django import forms

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2',)

