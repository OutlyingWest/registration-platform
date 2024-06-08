import time

from asgiref.sync import async_to_sync

from celery import shared_task

from .services import verify_document, UserDocumentRecognizer, UserFullNameVerifier


@shared_task(
    soft_time_limit=60 * 5,
    expires=60 * 10,
    ignore_result=True,
)
def verify_document_task(*args, **kwargs):
    verify_document(*args, **kwargs)


@shared_task(
    soft_time_limit=60 * 5,
    expires=60 * 10,
    ignore_result=True,
)
def recognize_document_task(*args, **kwargs):
    recognizer = UserDocumentRecognizer(*args, **kwargs)
    recognizer.extract_text()


@shared_task(
    soft_time_limit=60 * 5,
    expires=60 * 10,
    ignore_result=True,
)
def verify_user_full_name_task(*args, **kwargs):
    verifier = UserFullNameVerifier(*args, **kwargs)
    verifier.verify()
