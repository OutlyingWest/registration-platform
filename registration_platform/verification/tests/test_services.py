import os
import tempfile

import pytest
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile

from verification.models import UserDocument
from verification.services import UserDocumentRecognizer


def test_recognizer_set_text_path(document, remove_text_file_path_after):

    UserDocumentRecognizer.set_text_path(document)

    assert os.path.exists(document.extracted_text_file.path)
    text_file_name = os.path.basename(document.extracted_text_file.path).split('.')[0]
    expected_text_file_name = document.document_name
    assert text_file_name == expected_text_file_name
