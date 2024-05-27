import json

from channels.generic.websocket import AsyncWebsocketConsumer

from aiologger import Logger
from aiologger.levels import LogLevel
from aiologger.formatters.base import Formatter


class DocumentStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.logger = Logger.with_default_handlers(
            name=__name__,
            level=LogLevel.INFO,
            formatter=Formatter(
                fmt='%(levelname)s:     %(name)s %(message)s',
            )
        )
        await self.accept()
        user = self.scope['user']
        await self.channel_layer.group_add(f'user_{user.id}_document_update', self.channel_name)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def document_status_update(self, event):
        await self.logger.info(f'Event: document_id = {event["document_id"]} new_status = {event["new_status"]}')
        await self.send(text_data=json.dumps({
            'document_id': event['document_id'],
            'new_status': event['new_status']
        }))
