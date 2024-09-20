from django import forms
from .models import Prospect

class ProspectForm(forms.ModelForm):
    class Meta:
        model = Prospect
        fields = ['name', 'status', 'purpose', 'property_type', 'amount', 'context', 'sreo_document']  # Added 'sreo_document'