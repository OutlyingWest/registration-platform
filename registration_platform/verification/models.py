import os

from channels.db import database_sync_to_async
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from .utilities import build_document_path, build_document_text_path


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
    uploaded_file = models.FileField(upload_to=build_document_path, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'], message='Выберите файл в формате PDF')
    ], verbose_name="Файл", blank=True, default='')
    extracted_text_file = models.FileField(upload_to=build_document_text_path, verbose_name='Извлеченный текст',
                                           default='', blank=True)
    
    def save(self, *args, **kwargs):
        # Check does uploaded_file already exist
        if self.pk:
            old_document = UserDocument.objects.get(pk=self.pk)
            if old_document.uploaded_file and old_document.uploaded_file != self.uploaded_file:
                old_file_path = old_document.uploaded_file.path
                if os.path.isfile(old_file_path):
                    os.remove(old_file_path)

        super(UserDocument, self).save(*args, **kwargs)

    def update_status(self, status: str) -> None:
        self.status = status
        self.save(update_fields=('status',))

    def update_file(self, file) -> None:
        self.uploaded_file = file
        self.save(update_fields=('uploaded_file',))

    @classmethod
    def update_status_by_id(cls, document_id: int, status: str):
        document = cls.objects.get(id=document_id)
        document.update_status(status)
        return document

    @classmethod
    @database_sync_to_async
    def async_get_status_by_id(cls, document_id: int) -> status:
        document = cls.objects.get(id=document_id)
        return document.status

    @classmethod
    def update_document_file_by_id(cls, document_id: int, file):
        document = cls.objects.get(id=document_id)
        document.update_file(file)
        return document

    def get_filename(self):
        return os.path.basename(self.uploaded_file.name)
