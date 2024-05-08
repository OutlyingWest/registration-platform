from django.utils.deconstruct import deconstructible
import os


@deconstructible
class UserMediaSubPath:
    def __init__(self, sub_path: str, file_basename: str):
        self.sub_path = sub_path
        self.file_basename = file_basename

    def __call__(self, instance, filename):
        user_id = str(instance.user.id)
        extension = filename.split('.')[-1]
        return os.path.join('users', user_id, self.sub_path, self.file_basename, extension)
