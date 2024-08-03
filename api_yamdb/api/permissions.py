from django.conf import settings
from rest_framework.permissions import BasePermission
from rest_framework import permissions


class OnlyAdminAllowed(BasePermission):
    """Пермишен с доступом только для пользователей с ролью 'админ'."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == settings.ADMIN_ROLE
            or request.user.is_authenticated
            and request.user.is_staff is True
        )


class IsOwnerOrManagerOrReadOnly(BasePermission):
    """
    Пермишен включает в себя доступ для:

    - всех пользователей, если метод запроса безопасный
    - админа, модератора, суперюзера или владельца объекта для остальных
    методов.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user
            or request.user.role in settings.MANAGER_ROLES
        )


class AccountOwnerOrManager(IsOwnerOrManagerOrReadOnly):
    """
    Пермишен- наследник.

    Для любого метода требует аутентификацию, а также принадлежность объекта,
    или одну из ролей: администратор, модератор, суперюзер.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated
