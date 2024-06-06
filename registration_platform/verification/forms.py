from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory
from .models import UserDocument


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            'avatar',
            'first_name',
            'last_name',
            'patronymic',
            'gender',
            'birthday',
            'email',
        )
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'application/pdf'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birthday': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            # 'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UserDocumentForm(forms.ModelForm):
    class Meta:
        model = UserDocument
        fields = (
            'document_name',
            'status',
            'uploaded_file',
        )


UserDocumentsFormSet = modelformset_factory(UserDocument, form=UserDocumentForm, extra=0)
