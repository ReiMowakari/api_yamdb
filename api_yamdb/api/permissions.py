from rest_framework.permissions import (
    BasePermission, SAFE_METHODS)


class OnlyAdminAllowed(BasePermission):
    """
    Пермишен с доступом только для пользователей с ролью 'админ'
    и суперпользователя.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_superuser is True
            )
        )


class AdminOrReadOnly(BasePermission):
    """
    Пермишен для категорий, жанров, произведений.

    Безопасные методы доступны любому пользователю. Остальные методы только для
    Админа и суперпользователя.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.is_admin
            or request.user.is_superuser
        )


class AdminModeratorAuthorPermission(BasePermission):
    """
    Пермишен для отзывов и комментариев.

    Безопасные методы доступны любому пользователю. Остальные методы только для
    Админа, Модератора и Автора
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_manager
            or request.user.is_superuser
        )
