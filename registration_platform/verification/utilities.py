import os


def document_path(instance, filename):
    user_id = str(instance.user.id)
    extension = filename.split('.')[-1]
    file_basename = str(instance.document_name)
    return os.path.join('users', user_id, 'documents', file_basename, extension)

