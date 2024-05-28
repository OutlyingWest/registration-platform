import time

from asgiref.sync import async_to_sync

from celery import shared_task

from .services import document_status_send, verify_document


@shared_task(
    soft_time_limit=60 * 5,
    expires=60 * 10
)
def verify_document_task(*args, **kwargs):
    verify_document(*args, **kwargs)
