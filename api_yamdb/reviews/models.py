from django.db import models

from reviews.validations import validate_year


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
