from django.db.models import Avg
from rest_framework import serializers

from api_yamdb.settings import MIN_YEAR
from reviews.models import (
    Category,
    Genre,
    Review,
    Title
)
from reviews.utils import get_current_year
from reviews.validations import INCORRECT_TITLE_YEAR


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериалайзер произведений для методов на запись."""
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        required=False,
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=True
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category',
        )

    def validate_year(self, year):
        """Валидация для года."""
        if not (MIN_YEAR <= year <= get_current_year()):
            raise serializers.ValidationError(INCORRECT_TITLE_YEAR)
        return year


class TitleViewSerializer(serializers.ModelSerializer):
    """Сериалайзер произведений для методов на чтение."""
    genre = GenreSerializer(many=True, required=False,)
    category = CategorySerializer(required=True,)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )
        read_only_fields = fields

    def get_rating(self, obj):
        """Подсчет рейтинга произведения."""
        if not obj.reviews.count():
            review = Review.objects.filter(title=obj).aggregate(
                rating=Avg('score')
            )
            return review.get('rating')
        return None
