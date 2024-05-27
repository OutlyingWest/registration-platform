import os
from datetime import datetime


def document_path(instance, filename):
    user_id = str(instance.user.id)
    user_file_name, extension = filename.split('.')
    file_basename = str(instance.document_name)
    return os.path.join(
        'users',
        user_id,
        'documents',
        f'{file_basename}_{user_file_name}.{extension}'
    )


def document_text_path(document):
    user_id = str(document.user.id)
    file_basename = str(document.document_name)
    return os.path.join(
        'media',
        'users',
        user_id,
        'document_texts',
        f'{file_basename}.txt'
    )
