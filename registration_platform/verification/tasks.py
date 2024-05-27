import time

from asgiref.sync import async_to_sync

from celery import shared_task

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
    soft_time_limit=60 * 5,
    expires=60 * 7
)
def verify_document_task(*args, **kwargs):
    verify_document(*args, **kwargs)
