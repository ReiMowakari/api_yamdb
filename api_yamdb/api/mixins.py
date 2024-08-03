from rest_framework.serializers import (
    StringRelatedField
)


class CommonFieldsCommentReviewMixin:
    """
    Общий миксин для полей для исключения кода
    Для моделей Review и Comment.
    """

    author = StringRelatedField()

    class Meta:
        read_only_fields = ('id', 'author', 'pub_date')
