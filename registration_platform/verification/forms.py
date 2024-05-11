from django import forms
from django.forms import modelformset_factory
from .models import UserDocument


class DocumentForm(forms.ModelForm):
    class Meta:
        model = UserDocument
        fields = ['document_name', 'status', 'file']


DocumentFormSet = modelformset_factory(UserDocument, form=DocumentForm, extra=0)
