from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.conf import settings

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)
    access_code = forms.CharField(max_length=32, widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2', 'access_code')

    def clean_access_code(self):
        access_code = self.cleaned_data.get('access_code').strip()
        print(f"Entered access code: {access_code}")
        print(f"Expected access code: {settings.SIGNUP_ACCESS_CODE}")
        if access_code != settings.SIGNUP_ACCESS_CODE:
            raise forms.ValidationError("Invalid access code.")
        return access_code

