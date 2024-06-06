import os
from django.conf import settings


def build_document_path(document, filename):
    user_id = str(document.user.id)
    user_file_name, extension = filename.split('.')
    file_basename = str(document.document_name)
    return os.path.join(
        'users',
        user_id,
        'documents',
        f'{file_basename}_{user_file_name}.{extension}'
    )


def build_document_text_path(document, filename=''):
    user_id = str(document.user.id)
    file_basename = str(document.document_name)
    return os.path.join(
        'users',
        user_id,
        'document_texts',
        f'{file_basename}.txt'
    )
