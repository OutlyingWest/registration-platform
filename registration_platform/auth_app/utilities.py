import os


def file_path(instance, filename):
    user_id = str(instance.id)
    extension = filename.split('.')[-1]
    return os.path.join('users', user_id, 'avatar', extension)

