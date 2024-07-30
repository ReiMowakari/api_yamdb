from django.db import models


class Reviews(models.Model):
    """Модель для отзывов."""
    text = models.TextField('Содержимое отзыва')
    #author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    score = models.PositiveSmallIntegerField('Оценка', default=1)
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
        #constraints = models.UniqueConstraint(fields=['title', 'author'],name='unique_author_title')


class Comments(models.Model):
    """Модель для комментариев."""
    text = models.TextField('Содержимое комментария')
    #author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    review = models.ForeignKey(
        Reviews,
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
