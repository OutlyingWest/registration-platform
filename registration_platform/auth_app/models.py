from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import FileExtensionValidator, RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from .utilities import file_path


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    phone_regex_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                           message="Номер телефона должен быть в формате: '+99999999999'. "
                                                   "Допускается до 15 цифр.")
    avatar_extension_validator = FileExtensionValidator(allowed_extensions=['jpg', 'bmp', 'png'],
                                                        message='Выберите файл в формате jpg, bmp, png')

    patronymic = models.CharField(verbose_name='Отчество', max_length=150, blank=False)
    birthday = models.DateField(verbose_name='Дата рождения', blank=False, null=True)

    GENDER_CHOICES = [
        (1, 'Мужской'),
        (2, 'Женский')
    ]
    gender = models.PositiveSmallIntegerField(verbose_name='Пол', choices=GENDER_CHOICES, blank=False, null=True)
    email = models.EmailField(verbose_name='Email', unique=True)
    phone_number = models.CharField(verbose_name='Номер телефона', validators=[phone_regex_validator], max_length=17,
                                    blank=False)
    avatar = models.ImageField(verbose_name='Фото', blank=True,
                               upload_to=file_path,
                               validators=[avatar_extension_validator])

    username = models.CharField(
        max_length=150,
        unique=False,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name_plural = 'Участники'
        verbose_name = 'Участник'
        ordering = ['last_name']

    def natural_key(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse('account', kwargs={'user_id': self.pk})

    def __str__(self):
        return f'Участник {self.first_name} {self.last_name}: {self.email}'
