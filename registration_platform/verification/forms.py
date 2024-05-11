from django import forms
from .models import UserDocument


class DocumentForm(forms.ModelForm):
    class Meta:
        model = UserDocument
        fields = ['document_name', 'status', 'file']
