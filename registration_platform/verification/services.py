import asyncio
import time

from asgiref.sync import async_to_sync
from celery.signals import task_postrun
from channels.layers import get_channel_layer
from django.core.exceptions import ValidationError

from .models import UserDocument


def verify_document(document_id: int):
    channel_layer = get_channel_layer()
    document = UserDocument.update_status_by_id(document_id, 'in_progress')
    user_id = document.user.id
    # Send status through WebSocket
    async_to_sync(document_status_send)(user_id, document_id, 'В обработке', channel_layer)

    # Verification process placeholder
    time.sleep(10)

    document = UserDocument.objects.get(id=document_id)
    document.update_status('approved')
    # Send status through WebSocket
    async_to_sync(document_status_send)(user_id, document_id, 'Одобрен', channel_layer)


async def document_status_send(user_id: int, document_id: int, new_status: str, channel_layer=None):
    if not channel_layer:
        channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f'user_{user_id}_document_update',  # Group
        {
            'type': 'document.status.update',  # Method of consumer
            'document_id': document_id,
            'new_status': new_status
        }
    )

