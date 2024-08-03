from rest_framework import filters, mixins
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import (
    StringRelatedField
)


class CreateDestroyListNSIMixin(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Миксин для вьюсетов справочников.

    Справочниками на текущий момент являются:
    - Category (Категории)
    - Genre (Жанры)
    """
    filter_backends = (filters.SearchFilter, )
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination
    # TODO: permission_classes = (..., )
    search_field = ('name', )


class CommonFieldsCommentReviewMixin:
    """
    Общий миксин для полей для исключения кода
    Для моделей Review и Comment.
    """

    author = StringRelatedField()

    class Meta:
        read_only_fields = ('id', 'author', 'pub_date')
