import asyncio
import time

from asgiref.sync import async_to_sync

from celery import shared_task
from channels.layers import get_channel_layer

from .models import UserDocument
from .services import document_status_send, verify_document


@shared_task()
def add(x, y):
    return x + y


@shared_task()
def long(*args, **kwargs):
    time.sleep(15)
    async_to_sync(document_status_send(*args, **kwargs))
    return 'Long Task Done!'


@shared_task(
    soft_time_limit=15,
    expires=20
)
def verify_document_task(*args, **kwargs):
    verify_document(*args, **kwargs)
