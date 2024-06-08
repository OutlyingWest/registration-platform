from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserDocument


@receiver(post_save, sender=get_user_model())
def create_user_documents(sender, instance, created, **kwargs):
    if created:
        for doc_type, doc_name in UserDocument.DOCUMENT_TYPES:
            UserDocument.objects.create(
                user=instance,
                document_name=doc_type,
            )
