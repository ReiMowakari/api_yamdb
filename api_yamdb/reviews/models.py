from django.conf import settings
from django.core import validators
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.settings import (
    MIN_SCORE,
    MAX_SCORE,
)
from reviews.validations import validate_year


class CustomUser(AbstractUser):
    """
    Кастомная модель юзеров.

    Имеет кастомные поля:
    - 'role': для управления полномочиями.
    - 'confirmation_code': для выполнения процедуры регистрации.
    - 'bio': информация о пользователе.
    """

    ADMIN_ROLE = 'admin'
    MODERATOR_ROLE = 'moderator'
    USER_ROLE = 'user'

    MANAGER_ROLES = (ADMIN_ROLE, MODERATOR_ROLE)

    AVAILABLE_ROLES = [
        (ADMIN_ROLE, 'админ'),
        (MODERATOR_ROLE, 'модератор'),
        (USER_ROLE, 'обычный пользователь')
    ]

    role = models.CharField(
        choices=AVAILABLE_ROLES,
        default='user',
        max_length=16,
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

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN_ROLE

    @property
    def is_manager(self):
        return self.role in self.MANAGER_ROLES


class Category(models.Model):
    """Категории."""

    name = models.CharField(
        verbose_name='Наименование',
        max_length=256,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Код',
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'категорию'
        verbose_name_plural = 'Категории'
        default_related_name = 'categories'

    def __str__(self) -> str:
        """Представление объекта в виде строки."""
        return self.name[:10]


class Genre(models.Model):
    """Жанры."""

    name = models.CharField(
        verbose_name='Наименование',
        max_length=256,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Код',
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        default_related_name = 'genres'

    def __str__(self) -> str:
        """Представление объекта в виде строки."""
        return self.name[:10]


class TitleManager(models.Manager):
    """Менеджер для произведений."""
    def create_object(self, **extra_fields):
        category = extra_fields.get('category')
        obj_category = Category.objects.get(id=category)
        extra_fields.update(category=obj_category)

        title = self.model(**extra_fields)
        title.save(using=self._db)
        return title


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
        blank=True
    )
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

    objects = TitleManager()

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


class ReviewManager(models.Manager):
    """Менеджер для отзывов."""

    def create_object(self, **extra_fields):
        author = extra_fields.get('author')
        obj_author = CustomUser.objects.get(id=author)
        extra_fields.update(author=obj_author)

        review = self.model(**extra_fields)
        review.save(using=self._db)
        return review


class Review(models.Model):
    """Модель для отзывов."""

    text = models.TextField('Содержимое отзыва')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        default=1,
        validators=[
            MinValueValidator(
                MIN_SCORE,
                message='Оценка не может быть меньше 1'),
            MaxValueValidator(
                MAX_SCORE,
                message='Оценка не может быть больше 10')
        ]
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    objects = ReviewManager()

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


class CommentManager(ReviewManager):
    """Менеджер для комментариев."""

    pass


class Comment(models.Model):
    """Модель для комментариев."""

    text = models.TextField('Содержимое комментария')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    objects = CommentManager()

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ['-pub_date']
