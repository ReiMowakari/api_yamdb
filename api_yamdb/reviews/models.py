from django.core import validators
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser, Group
from django.db import models

from reviews.validations import validate_year


def get_default_role():
    """Функция возвращает id роли user из модели Group."""
    group, created = Group.objects.get_or_create(name='user')
    return group


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
        if not self.role:
            self.role = get_default_role()
        else:
            self.role = Group.objects.get(name=self.role)
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.username


class Category(models.Model):
    """Категории."""

    name = models.CharField(
        verbose_name='Наименование',
        max_length=256,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Код',
        max_length=128,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'категорию'  # ВП для админки
        verbose_name_plural = 'Категории'
        default_related_name = 'categories'

    def __str__(self) -> str:
        """Представление объекта в виде строки."""
        return self.name[:10]


class Genre(models.Model):
    """Жанры."""

    name = models.CharField(
        verbose_name='Наименование',
        max_length=256,  # Существуют такие жанры, длина которых > 100с
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Код',
        max_length=128,
        unique=True
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'жанр'  # ВП для админки
        verbose_name_plural = 'Жанры'
        default_related_name = 'genres'

    def __str__(self) -> str:
        """Представление объекта в виде строки."""
        return self.name[:10]


class Title(models.Model):
    """Произведения."""

    name = models.CharField(
        verbose_name='Наименование',
        max_length=256,
    )
    year = models.PositiveIntegerField(
        verbose_name='Год',
        validators=(validate_year,)
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=256,
        blank=True
    )
    # TODO: Перед сливом в master нужно убедиться, что есть rating
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='Жанр',
    )

    class Meta:
        verbose_name = 'произведение'  # ВП для админки
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'


class GenreTitle(models.Model):
    """Промежуточная сущность между произведениями и жанрами."""

    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'genre',),
                name='unique_genre_title'
            )
        ]
        verbose_name = 'связь произведения и жанра'  # ВП для админки
        verbose_name_plural = 'Связь произведения и жанра'
        default_related_name = 'genre_titles'


class Review(models.Model):
    """Модель для отзывов."""

    text = models.TextField('Содержимое отзыва')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name='Автор')
    score = models.PositiveSmallIntegerField(
        'Оценка', default=1, validators=[
            MinValueValidator(1, message='Оценка не может быть меньше 1'),
            MaxValueValidator(10, message='Оценка не может быть больше 10')])
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name='Произведение')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        ordering = ['-pub_date']
        # Ограничения на то, что можно оставить только один отзыв
        # к произведению от одного автора, а также ограничение на проверку
        # оценки в диапазоне от 1 до 10.
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_review_author_title'),
        ]


class Comment(models.Model):
    """Модель для комментариев."""

    text = models.TextField('Содержимое комментария')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name='Автор')
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ['-pub_date']
