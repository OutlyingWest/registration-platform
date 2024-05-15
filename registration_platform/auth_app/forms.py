from django.contrib.auth.forms import UserCreationForm
from .models import User


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
