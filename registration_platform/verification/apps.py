from django.apps import AppConfig


class VerificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'verification'
    verbose_name = 'Документы и Верификация'

    def ready(self):
        from .signals import create_user_documents
