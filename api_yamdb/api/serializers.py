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

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, required=False,)
    category = CategorySerializer(required=True,)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )

    def get_rating(self, obj):
        """Подсчет рейтинга произведения."""
        if not obj.reviews.count():
            return Review.objects.filter(title=obj).aggregate(
                rating=Avg('score')
            ).get('rating')
        return None

    def validate_year(self, year):
        """Валидация для года."""
        if not (MIN_YEAR <= year <= get_current_year()):
            raise serializers.ValidationError(INCORRECT_TITLE_YEAR)
        return year
