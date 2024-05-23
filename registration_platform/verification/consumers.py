import json

from channels.generic.websocket import AsyncWebsocketConsumer

from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from .models import UserDocument
from .services import document_status_send


class DocumentStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add('document_status_update', self.channel_name)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        document_id = int(data['document_id'].split('-')[1])
        await UserDocument.async_update_status_by_id(document_id, 'in_progress')
        channel_layer = get_channel_layer()
        await document_status_send(document_id, 'В обработке')

    async def document_status_update(self, event):
        print(f'{event}')
        await self.send(text_data=json.dumps({
            'document_id': event['document_id'],
            'new_status': event['new_status']
        }))



