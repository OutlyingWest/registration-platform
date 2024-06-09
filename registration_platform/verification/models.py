import os
from enum import Enum

from channels.db import database_sync_to_async
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from .utilities import build_document_path, build_document_text_path


class DocumentType(Enum):
    SNILS = 'СНИЛС'
    PASSPORT = 'Паспорт'
    NAME_CHANGE = 'Документ о перемене имени'
    MARRIAGE_OR_DIVORCE = 'Документ о заключении или расторжении брака'
    OTHER_DOCUMENT_1 = 'Иной документ 1'
    BACHELORS_DIPLOMA = 'Диплом бакалавра'
    MASTERS_DIPLOMA = 'Диплом магистра'
    EMPLOYMENT_HISTORY = 'Трудовая книжка'
    ADVANCED_TRAINING_CERTIFICATE = 'Сертификат о повышении квалификации'
    OTHER_DOCUMENT_2 = 'Иной документ 2'
    NRS = 'НРС'
    DATA_PROCESSING_AGREEMENT = 'Согласие на обработку данных'

    @property
    def name(self):
        return self._name_.lower()

    @classmethod
    def choices(cls):
        return [(status.name, status.value) for status in cls]


class DocumentStatus(Enum):
    NOT_UPLOADED = 'Не загружен'
    IN_PROGRESS = 'В обработке'
    VERIFICATION_FAILED = 'Проверка не пройдена'
    APPROVED = 'Одобрен'

    @property
    def name(self):
        return self._name_.lower()

    @classmethod
    def choices(cls):
        return [(status.name, status.value) for status in cls]


class UserDocument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=100, choices=DocumentType.choices(), verbose_name="Тип документа")
    status = models.CharField(max_length=20, default='not_uploaded', choices=DocumentStatus.choices(),
                              verbose_name="Статус")
    uploaded_file = models.FileField(upload_to=build_document_path, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'], message='Выберите файл в формате PDF')
    ], verbose_name="Файл", blank=True, default='')
    extracted_text_file = models.FileField(upload_to=build_document_text_path, verbose_name='Извлеченный текст',
                                           default='', blank=True)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'

    def save(self, *args, **kwargs):
        # Check does uploaded_file already exist
        if self.pk:
            old_document = UserDocument.objects.get(pk=self.pk)
            old_file_path = None
            print(f'From save')
            print(f'{old_document.extracted_text_file=}')
            print(f'{self.extracted_text_file=}')
            if old_document.extracted_text_file and old_document.extracted_text_file != self.extracted_text_file:
                self.remove_old_file(old_document.extracted_text_file.path)

            if old_document.uploaded_file and old_document.uploaded_file != self.uploaded_file:
                self.remove_old_file(old_document.uploaded_file.path)

        super(UserDocument, self).save(*args, **kwargs)

    @staticmethod
    def remove_old_file(old_file_path):
        if old_file_path:
            print(f'{old_file_path=}')
            if os.path.isfile(old_file_path):
                os.remove(old_file_path)

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
