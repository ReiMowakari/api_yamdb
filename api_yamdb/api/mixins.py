from rest_framework import filters, mixins
from rest_framework.pagination import LimitOffsetPagination


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
