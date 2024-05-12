from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from .utilities import document_path


class UserDocument(models.Model):
    DOCUMENT_TYPES = [
        ('snils', 'СНИЛС'),
        ('passport', 'Паспорт'),
        ('name_change', 'Документ о перемене имени'),
        ('marriage_or_divorce', 'Документ о заключении или расторжении брака'),
        ('other_document_1', 'Иной документ 1'),
        ('bachelors_diploma', 'Диплом бакалавра'),
        ('masters_diploma', 'Диплом магистра'),
        ('employment_history', 'Трудовая книжка'),
        ('advanced_training_certificate', 'Сертификат о повышении квалификации'),
        ('other_document_2', 'Иной документ 2'),
        ('nrs', 'НРС'),
        ('data_processing_agreement', 'Согласие на обработку данных')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=100, choices=DOCUMENT_TYPES, verbose_name="Тип документа")
    status = models.CharField(max_length=20, default='not_uploaded', choices=[
        ('not_uploaded', 'Не загружен'),
        ('in_progress', 'В обработке'),
        ('verification_failed', 'Проверка не пройдена'),
        ('approved', 'Одобрен'),
    ], verbose_name="Статус")
    file = models.FileField(upload_to=document_path, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'], message='Выберите файл в формате PDF')
    ], verbose_name="Файл")
