from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

from api.filters import TitleFilterSet
from api.mixins import CreateDestroyListNSIMixin
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
    CreateDestroyListNSIMixin,
    viewsets.GenericViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(
    CreateDestroyListNSIMixin,
    viewsets.GenericViewSet
):
    queryset = Genre.objects.all()
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
