import os
from pprint import pprint

import pytest

from verification.services import UserDocumentRecognizer, SpecialityVerifier, SpecialityCol


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

