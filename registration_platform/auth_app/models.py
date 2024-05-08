from django.core.validators import FileExtensionValidator, RegexValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

from .utilities import UserMediaSubPath


class User(AbstractUser):
    phone_regex_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                           message="Номер телефона должен быть в формате: '+999999999'. "
                                                   "Допускается до 15 цифр.")
    avatar_extension_validator = FileExtensionValidator(allowed_extensions=['jpg', 'bmp', 'png'],
                                                        message='Выберите файл в формате jpg, bmp, png')

    patronymic = models.CharField(verbose_name='Отчество', max_length=150, blank=False)
    birthday = models.DateField(verbose_name='Дата рождения', blank=False, null=True)

    gen = [
        (1, 'Мужской'),
        (2, 'Женский')
    ]
    gender = models.PositiveSmallIntegerField(verbose_name='Пол', choices=gen, blank=False)
    email = models.EmailField(verbose_name='Email', unique=True)
    phone_number = models.CharField(verbose_name='Номер телефона', validators=[phone_regex_validator], max_length=17,
                                    blank=False)
    avatar = models.ImageField(verbose_name='Фото', blank=True,
                               upload_to=UserMediaSubPath(sub_path='', file_basename='avatar'),
                               validators=[avatar_extension_validator])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name_plural = 'Участники'
        verbose_name = 'Участник'
        ordering = ['last_name']

    def natural_key(self):
        return self.get_full_name()

    def __str__(self):
        return f'Участник {self.first_name} {self.last_name}: {self.email}'


class UserDocuments(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents', null=True)
    file_extension_validator = FileExtensionValidator(allowed_extensions=['pdf'],
                                                      message='Выберите файл в формате PDF')

    snils = models.FileField(verbose_name='СНИЛС', blank=False,
                             upload_to=UserMediaSubPath(sub_path='documents', file_basename='snils'),
                             validators=[file_extension_validator])
    inn = models.CharField(verbose_name='ИНН', max_length=150, blank=True)
    passport = models.FileField(verbose_name='Паспорт', blank=False,
                                upload_to=UserMediaSubPath(sub_path='documents', file_basename='passport'),
                                validators=[file_extension_validator])
    name_change = models.FileField(verbose_name='Документ о перемене имени', blank=True,
                                   upload_to=UserMediaSubPath(sub_path='documents',
                                                              file_basename='name_change'),
                                   validators=[file_extension_validator])
    marriage_or_divorce = models.FileField(verbose_name='Документ о заключении или расторжении брака', blank=True,
                                           upload_to=UserMediaSubPath(sub_path='documents',
                                                                      file_basename='marriage_or_divorce'),
                                           validators=[file_extension_validator])
    other_document_1 = models.FileField(verbose_name='Иной документ', blank=True,
                                        upload_to=UserMediaSubPath(sub_path='documents',
                                                                   file_basename='other_document_1'),
                                        validators=[file_extension_validator])
    bachelors_diploma = models.FileField(verbose_name='Диплом бакалавра', blank=False,
                                         upload_to=UserMediaSubPath(sub_path='documents',
                                                                    file_basename='bachelors_diploma'),
                                         validators=[file_extension_validator])
    masters_diploma = models.FileField(verbose_name='Диплом магистра', blank=True,
                                       upload_to=UserMediaSubPath(sub_path='documents',
                                                                  file_basename='masters_diploma'),
                                       validators=[file_extension_validator])
    employment_history = models.FileField(verbose_name='Трудовая книжка', blank=False,
                                          upload_to=UserMediaSubPath(sub_path='documents',
                                                                     file_basename='employment_history'),
                                          validators=[file_extension_validator])
    advanced_training_certificate = models.FileField(verbose_name='Сертификат о повышении квалификации ', blank=True,
                                                     upload_to=UserMediaSubPath(sub_path='documents',
                                                                                file_basename='advanced_training_'
                                                                                              'certificate'),
                                                     validators=[file_extension_validator])
    other_document_2 = models.FileField(verbose_name='Иной документ', blank=True,
                                        upload_to=UserMediaSubPath(sub_path='documents',
                                                                   file_basename='other_document_2'),
                                        validators=[file_extension_validator])

    nrs_options = [
        (1, 'Уведомление о включении в НРС НОСТРОЙ'),
        (2, 'Уведомление о включении в НРС НОПРИЗ')
    ]
    which_nrs = models.PositiveSmallIntegerField(verbose_name='Пол', choices=nrs_options, blank=False)
    nrs = models.FileField(verbose_name='Ваш НРС', blank=False,
                           upload_to=UserMediaSubPath(sub_path='documents', file_basename='nrs'),
                           validators=[file_extension_validator])

    data_processing_agreement = models.FileField(verbose_name='Согласие на обработку данных', blank=False,
                                                 upload_to=UserMediaSubPath(sub_path='documents',
                                                                            file_basename='data_processing_agreement'),
                                                 validators=[file_extension_validator])
