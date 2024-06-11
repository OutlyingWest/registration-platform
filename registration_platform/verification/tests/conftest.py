import os
import sys
import tempfile

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model

from verification.utilities import build_document_text_path, build_document_path
from verification.services import UserDocumentRecognizer, SpecialityVerifier
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
def remove_uploaded_file_path_after(document, document_name_arg):
    if document_name_arg == 'not_document':
        return
    document_path = build_document_path(document, f'{document_name_arg}.pdf')
    media_document_path = os.path.join(settings.MEDIA_ROOT, document_path)
    yield media_document_path
    os.remove(media_document_path)

@pytest.fixture
def remove_text_file_path_after(document):
    text_path = build_document_text_path(document)
    media_text_path = os.path.join(settings.MEDIA_ROOT, text_path)
    yield media_text_path
    os.remove(media_text_path)


@pytest.fixture
def specialities(document):
    verifier = SpecialityVerifier(document.id)
    specs = verifier.load_specialities()
    return specs


@pytest.fixture
def extracted_text(document):
    text_path = UserDocumentRecognizer.set_text_path(document)
    load_text = [
        'Наименование учебных предметов\n',
        'Итоговая отметка\n',
        'Ядерная энергетика и теплофизика\n',
    ]
    with open(text_path, 'w') as f:
        f.writelines(load_text)
    expected_text = [line.strip() for line in load_text]
    return text_path, expected_text


def pytest_addoption(parser):
    parser.addoption('--document', action='store', default='not_document', help='Document name')


@pytest.fixture
def document_name_arg(request):
    return request.config.getoption('--document')
