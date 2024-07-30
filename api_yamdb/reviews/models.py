from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """Модель для отзывов."""
    text = models.TextField('Содержимое отзыва')
    #author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    score = models.IntegerField('Оценка', default=1, validators=[
        MinValueValidator(1), MaxValueValidator(10)
    ])
    #title = models.ForeignKey(Title,on_delete=models.CASCADE, verbose_name='Произведение')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        ordering = ['-pub_date']
        # Ограничения на то, что можно оставить только один отзыв к произведению
        # от одного автора, а также ограничение на проверку оценки в диапазоне от 1 до 10.
        #constraints = [
        # models.UniqueConstraint(fields=['title', 'author'],
        # name='unique_author_title'),
        # models.CheckConstraint(check=(F('score') >= 1) & (F('score') <= 10),
        # name='check_range_score')
        # ]


class Comment(models.Model):
    """Модель для комментариев."""
    text = models.TextField('Содержимое комментария')
    #author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ['-pub_date']
