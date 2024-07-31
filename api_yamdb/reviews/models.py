from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractUser, Group


def get_default_role():
    """Функция возвращает id роли user из модели Group."""
    group, created = Group.objects.get_or_create(name='user')
    return group.pk


class CustomUser(AbstractUser):
    """
    Кастомная модель юзеров.

    Имеет one-to-many на модель Group для разаграничения доступа юзерам.
    """

    groups = None
    role = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='роль',
        max_length=16,
        help_text='Роль пользователя, определяющая доступ к ресурсам проекта'
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Электронный адрес',
        unique=True,
        validators=[validators.validate_email]
    )
    confirmation_code = models.CharField(
        'Код подтверждения', max_length=50, blank=True, null=True
    )
    bio = models.TextField(
        blank=True, verbose_name='О себе',
    )

    class Meta:
        verbose_name = 'пользователя'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', '-date_joined')
        default_related_name = 'users'

    def save(self, *args, **kwargs):
        self.clean()
        if not self.role:
            self.role = get_default_role()
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    # TODO Проверку существования объекта модели Group.