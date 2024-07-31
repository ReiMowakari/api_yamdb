from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

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
