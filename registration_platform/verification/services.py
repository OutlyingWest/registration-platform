import asyncio

from channels.layers import get_channel_layer

from .models import UserDocument


async def verify_document(document: UserDocument):
    # Verification process placeholder
    await asyncio.sleep(10)
    await document.async_update_status_by_id(document.id, 'approved')
    # Send status through WebSocket
    await document_status_send(document.user.id, document.id, 'Одобрен')
    return document


async def document_status_send(user_id: int, document_id: int, new_status: str):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f'user_{user_id}_document_update',  # Group
        {
            'type': 'document.status.update',  # Method of consumer
            'document_id': document_id,
            'new_status': new_status
        }
    )
