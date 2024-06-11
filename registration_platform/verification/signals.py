from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import DocumentName, UserDocument


@receiver(post_save, sender=get_user_model())
def create_user_documents(sender, instance, created, **kwargs):
    if created:
        for document_type in DocumentName:
            UserDocument.objects.create(
                user=instance,
                document_name=document_type.name,
            )
