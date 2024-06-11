import os
from pathlib import Path
from pprint import pprint

import pytest
from django.core.files import File
from django.conf import settings
from rapidfuzz import fuzz

from verification.services import UserDocumentRecognizer, SpecialityVerifier, SpecialityCol
from verification.models import DocumentName

from verification.models import UserDocument
from verification.utilities import build_document_path, build_document_text_path


def test_recognizer_set_text_path(document, remove_text_file_path_after):

    UserDocumentRecognizer.set_text_path(document)

    assert os.path.exists(document.extracted_text_file.path)
    text_file_name = os.path.basename(document.extracted_text_file.path).split('.')[0]
    expected_text_file_name = document.document_name
    assert text_file_name == expected_text_file_name


def test_load_specialities(document):
    specs = SpecialityVerifier.load_specialities()
    assert type(specs) == list


def test_load_document_text(extracted_text, remove_text_file_path_after):
    text_path, expected_text = extracted_text
    test_text = SpecialityVerifier.load_extracted_text(text_path)
    pprint(test_text)
    assert expected_text == test_text


def test_recognition_quality(user,
                             document_name_arg,
                             remove_text_file_path_after,
                             remove_uploaded_file_path_after):
    if document_name_arg == 'not_document':
        return

    if document_name_arg in DocumentName.get_names():
        pass
    else:
        return ValueError('Wrong document name')

    pdf_document_full_name = f'{document_name_arg}.pdf'
    document = UserDocument.objects.get(user=user.id, document_name=document_name_arg)

    path_document = Path().absolute() / 'registration_platform' / 'verification' / 'tests' / 'data' / 'documents'
    path_document_text = settings.MEDIA_ROOT / build_document_text_path(document)
    path_benchmark_texts = (
            Path().absolute() / 'registration_platform' / 'verification' / 'tests' / 'data' / 'benchmark_texts'
    )

    print(f'{path_document.as_posix()=}')
    print(f'{path_benchmark_texts.as_posix()=}')

    with open(path_document / pdf_document_full_name, 'rb') as f:
        document.uploaded_file = File(f, pdf_document_full_name)
        document.save()

    print(f'{document.uploaded_file.name=}')
    print(f'{document.uploaded_file.path=}')

    recognizer = UserDocumentRecognizer(document.id)
    recognizer.extract_text()

    print(f'{recognizer.text_path=}')

    with open(path_document_text, 'r') as f:
        extracted_text = f.read()
    print('extracted_text:')
    pprint(extracted_text)
    print('\n')

    txt_document_full_name = f'{document_name_arg}.txt'
    with open(path_benchmark_texts / txt_document_full_name, 'r') as f:
        benchmark_text = f.read()
    print('benchmark_text:')
    pprint(benchmark_text)

    token_set_ratio_score = fuzz.token_set_ratio(extracted_text, benchmark_text)
    print(f'\nAccuracy: {token_set_ratio_score:.2f}%')




