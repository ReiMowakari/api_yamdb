from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

from api.filters import TitleFilterSet
from api.mixins import CreateDestroyListNSIMixin
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleViewSerializer,
    CommentSerializer,
    ReviewSerializer,
)
from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
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


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    # permission_classes = ()

    def get_review(self):
        """Получение объекта отзыва."""
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        return review

    def get_queryset(self):
        return self.get_review().comments

    def perform_create(self, serializer):
        serializer.save(review=self.get_review(), author=self.request.user)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    # permission_classes = ()

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title=title_id)

    def perform_create(self, serializer):
        user = self.request.user
        score = self.request.data.get('score')
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(title=title, author=user, score=score)
