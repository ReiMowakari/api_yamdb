from django.conf import settings
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .mixins import (
    CommonUserSerializerFieldsMixin,
    CommonReviewCommentSerializerMixin,
    CommonCategoryGenreSerializerMixin,
)
from .validators import (
    validate_username_allowed,
    validate_data_unique_together,
    validate_confirmation_code,
    validate_score,
)
from api_yamdb.settings import MIN_YEAR
from reviews.models import (
    Category,
    Comment,
    CustomUser,
    Genre,
    Review,
    Title,
)
from reviews.validations import INCORRECT_TITLE_YEAR
from reviews.utils import get_current_year


class CategorySerializer(
    CommonCategoryGenreSerializerMixin, serializers.ModelSerializer
):
    """Сериалайзер для категорий."""

    class Meta(CommonCategoryGenreSerializerMixin.Meta):
        model = Category


class GenreSerializer(
    CommonCategoryGenreSerializerMixin, serializers.ModelSerializer
):
    """Сериалайзер для жанров."""

    class Meta(CommonCategoryGenreSerializerMixin.Meta):
        model = Genre


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
        if obj.reviews.count():
            review = Review.objects.filter(title=obj).aggregate(
                rating=Avg('score')
            )
            return review.get('rating')
        return None


class CommentSerializer(
    CommonReviewCommentSerializerMixin, serializers.ModelSerializer
):
    """Сериалайзер для комментариев."""

    author = serializers.StringRelatedField(
        source='author.username'
    )

    class Meta(CommonReviewCommentSerializerMixin.Meta):
        model = Comment


class ReviewSerializer(
    CommonReviewCommentSerializerMixin, serializers.ModelSerializer
):
    """Сериалайзер для Отзывов."""

    score = serializers.IntegerField(required=True)
    author = serializers.StringRelatedField(
        source='author.username'
    )

    def create(self, validated_data):
        """
        Валидация при создании объекта отзыва.
        - Проверка на уже существующий отзыв.
        - Проверка на соответствие оценки.
        """
        author = validated_data.get('author')
        title = validated_data.get('title')
        score = validated_data.get('score')
        if Review.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError(
                'Такой отзыв уже существует.')
        # Проверка на соответствие оценки.
        validate_score(int(score))
        return super().create(validated_data)

    class Meta(CommonReviewCommentSerializerMixin.Meta):
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class SelfUserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализация данных для создания нового юзера.

    Работает только с post запросами.
    """

    username = serializers.CharField(
        required=True
    )
    email = serializers.EmailField(
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        validate_username_allowed(username)
        validate_data_unique_together(username, email)
        return data


class AdminUserSerializer(
    CommonUserSerializerFieldsMixin, SelfUserRegistrationSerializer
):
    """Сериализатор для работы с запросами от пользователей с ролью админ."""

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
    )

    role = serializers.ChoiceField(
        choices=settings.AVAILABLE_ROLES, required=False
    )


class GetOrPatchUserSerializer(
    CommonUserSerializerFieldsMixin, serializers.ModelSerializer
):
    """
    Сериализатор для работы с запросами на изменение профиля пользователя.
    """

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
        required=False
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
        required=False
    )

    class Meta(CommonUserSerializerFieldsMixin.Meta):
        read_only_fields = ('role',)


class ObtainTokenSerializer(serializers.ModelSerializer):

    username = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        # Проверка confirmation_code для пользователя.
        validate_confirmation_code(username, confirmation_code)
        return data
