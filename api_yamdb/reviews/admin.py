from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Кастомная Админка пользователя."""

    fieldsets = (
        (None, {'fields': ('username',)}),
        ('Данные пользователя', {
            'fields': ('first_name', 'last_name', 'email', 'bio',)
        }),
        ('Привелегии', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser',)
        }),
    )

    list_display = (
        'username',
        'email',
        'role',
        'is_staff',
    )

    list_editable = (
        'is_staff',
    )

    search_fields = (
        'username',
        'email'
    )

    list_filter = (
        'is_staff',
        'role'
    )

    empty_value_display = 'Нет данных.'
