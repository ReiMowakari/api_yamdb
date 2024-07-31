from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ObjectDoesNotExist


class CustomUser(AbstractUser):
    """Кастомная модель юзеров. Имеет one-to-many на модель Group
    для разаграничения доступа юзерам.
    """
    groups = None

    @staticmethod
    def get_default_role():
        """Классовый метод возвращающий id роли user из модели Group."""
        try:
            return Group.objects.get(name='user').id
        except ObjectDoesNotExist:
            return None

    role = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='роль',
        related_name='users',
        default=get_default_role(),
        max_length=16,
        help_text='Роль пользователя, определяющая доступ к ресурсам проекта.'
    )
    bio = models.TextField(blank=True, verbose_name='биография')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', 'date_joined')

    def __str__(self):
        return self.username

    # TODO Проверку существования объекта модели Group.
