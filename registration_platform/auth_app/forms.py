from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'patronymic',
            'gender',
            'birthday',
            'email',
            'phone_number',
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birthday': forms.TextInput(attrs={'class': 'form-control'}),
            #'email': forms.TextInput(attrs={'class': 'form-control'}),
            #'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
