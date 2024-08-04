from django.conf import settings
from rest_framework.permissions import (
    BasePermission, SAFE_METHODS)


class OnlyAdminAllowed(BasePermission):
    """Пермишен с доступом только для пользователей с ролью 'админ'."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.role == settings.ADMIN_ROLE
                or request.user.is_superuser is True
            )
        )


class IsOwnerOrManagerOrReadOnly(BasePermission):
    """
    Пермишен включает в себя доступ для:

    - всех пользователей, если метод запроса безопасный
    - админа, модератора, суперюзера или владельца объекта для остальных
    методов.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and (
                obj.author == request.user
                or request.user.role in settings.MANAGER_ROLES
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
            and request.user.role == settings.ADMIN_ROLE
            or request.user.is_authenticated
            and request.user.is_staff is True
        )


class AdminModeratorAuthorPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.role in settings.MANAGER_ROLES
        )
