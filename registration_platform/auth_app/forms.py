from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'avatar',
            'first_name',
            'last_name',
            'patronymic',
            'gender',
            'birthday',
            'email',
        )
