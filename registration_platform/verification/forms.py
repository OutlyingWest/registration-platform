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


class UserDocumentForm(forms.ModelForm):
    document_name_text = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={'readonly': True})
    )

    class Meta:
        model = UserDocument
        fields = (
            'document_name',
            'status',
            'file',
        )
        widgets = {
            'document_name': forms.HiddenInput(),
            'file': forms.FileInput(attrs={'accept': 'application/pdf'}),
            'status': forms.HiddenInput(),
        }


UserDocumentsFormSet = modelformset_factory(UserDocument, form=UserDocumentForm, extra=0)
