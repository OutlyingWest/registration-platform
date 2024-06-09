from django.contrib import admin

from .models import UserDocument


class UserDocumentsInline(admin.TabularInline):
    model = UserDocument
    extra = 0


admin.site.register(UserDocument)
