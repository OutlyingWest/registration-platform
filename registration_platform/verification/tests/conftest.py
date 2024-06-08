import os
import sys
import tempfile

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model

from verification.utilities import build_document_text_path
from verification.services import UserDocumentRecognizer
from verification.models import UserDocument


@pytest.fixture
def user(db):
    user_model = get_user_model()
    user = user_model.objects.create(
        id=sys.maxsize,
        password='12345',
        is_superuser=False,
        username='',
        first_name='Хы',
        last_name='Хо',
        is_staff=False,
        is_active=True,
        patronymic='Ха',
        gender=1,
        email='aoaoao@mail.ru',
        phone_number='+77777777777'
    )
    yield user


@pytest.fixture
def document(db, user):
    return UserDocument.objects.filter(user=user.id).first()


@pytest.fixture
def remove_text_file_path_after(document):
    text_path = build_document_text_path(document)
    media_text_path = os.path.join(settings.MEDIA_ROOT, text_path)
    yield media_text_path
    os.remove(media_text_path)
