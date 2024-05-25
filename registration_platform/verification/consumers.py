import json

from channels.generic.websocket import AsyncWebsocketConsumer

from .models import UserDocument
from .services import document_status_send


class DocumentStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        user = self.scope['user']
        await self.channel_layer.group_add(f'user_{user.id}_document_update', self.channel_name)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def document_status_update(self, event):
        print(f'{event=}')
        await self.send(text_data=json.dumps({
            'document_id': event['document_id'],
            'new_status': event['new_status']
        }))
