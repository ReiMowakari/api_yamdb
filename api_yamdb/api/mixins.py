from rest_framework import filters, mixins
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED

from .permissions import AdminOrReadOnly
from reviews.models import CustomUser

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
    permission_classes = (AdminOrReadOnly, )
    search_fields = ('name', )


class NoPutMethodMixin:
    """
    Общий миксин для исключения PUT запроса.
    """

    def update(self, request, *args, **kwargs):
        if not kwargs.get('partial', False):
            return Response(status=HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


class CommonUserSerializerFieldsMixin:
    """Миксин для исключения повторения полей сериалайзера для User."""
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class CommonReviewCommentSerializerMixin:
    """
    Миксин для исключения повторения полей сериалайзера
    для Comment и Review.
    """
    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')


class CommonCategoryGenreSerializerMixin:
    """
    Миксин для исключения повторения полей сериалайзера
    для Category и Genre.
    """
    class Meta:
        fields = ('name', 'slug',)