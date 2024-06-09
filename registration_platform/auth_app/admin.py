from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from verification.admin import UserDocumentsInline


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', )
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', )
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('password', )}),
        ('Персональные данные', {
            'fields': (
                'last_name',
                'first_name',
                'patronymic',
                'email',
                'phone_number',
                'gender',
                'birthday',
            )
        }),
        ('Права', {
            'fields': (
                'is_staff',
                'is_active',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Даты', {
            'fields': (
                'last_login',
                'date_joined',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'patronymic',
                'birthday',
                'gender',
                'phone_number',
                'is_staff',
                'is_active',
            )
        }),
    )

    # Add User's Documents from verification app to User's detailed webpage
    inlines = [UserDocumentsInline]


admin.site.register(User, CustomUserAdmin)
admin.site.site_header = 'Управление авторизацией'
