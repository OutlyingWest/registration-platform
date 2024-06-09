from django.apps import AppConfig


class VerificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'verification'
    verbose_name = 'Верификация Документов'

    def ready(self):
        from .signals import create_user_documents
