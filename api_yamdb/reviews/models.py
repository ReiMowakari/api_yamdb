from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

from reviews.validations import validate_year


User = get_user_model()


class Review(models.Model):
    """Модель для отзывов."""

    text = models.TextField('Содержимое отзыва')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
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
        # Ограничения на то, что можно оставить только один отзыв к произведению
        # от одного автора, а также ограничение на проверку оценки в диапазоне от 1 до 10.
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_review_author_title'),
        ]


class Comment(models.Model):
    """Модель для комментариев."""
    text = models.TextField('Содержимое комментария')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
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

        
class Category(models.Model):
    """Категории."""

    # TODO: Возможно, стоит вынести name и связное с ним в миксин?..
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
