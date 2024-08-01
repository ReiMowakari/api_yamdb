from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

from api.filters import TitleFilterSet
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleViewSerializer,
)
from reviews.models import (
    Category,
    Genre,
    Title,
)


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    filter_backends = (filters.SearchFilter, )
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination
    # TODO: permission_classes = (..., )
    queryset = Category.objects.all()
    search_field = ('name', )
    serializer_class = CategorySerializer


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    filter_backends = (filters.SearchFilter, )
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination
    # TODO: perimission_classes = (..., )
    queryset = Genre.objects.all()
    search_field = ('name', )
    serializer_class = GenreSerializer


class TitleViewSet(
    viewsets.ModelViewSet
):
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilterSet
    pagination_class = LimitOffsetPagination
    # TODO: perimission_classes = (..., )
    queryset = Title.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return TitleReadSerializer
        return TitleViewSerializer
