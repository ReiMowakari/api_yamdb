from django.conf import settings
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .validators import (
    validate_username_allowed,
    validate_data_unique_together,
    validate_confirmation_code
)
from .mixins import CommonFieldsCommentReviewMixin
from api_yamdb.settings import MIN_YEAR
from reviews.models import (
    Category,
    Genre,
    Review,
    Title,
    CustomUser,
)
from reviews.validations import INCORRECT_TITLE_YEAR
from reviews.utils import get_current_year


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


class CommentSerializer(CommonFieldsCommentReviewMixin, ModelSerializer):

    class Meta(CommonFieldsCommentReviewMixin.Meta):
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class ReviewSerializer(CommonFieldsCommentReviewMixin, ModelSerializer):
    score = IntegerField(required=True)

    class Meta(CommonFieldsCommentReviewMixin.Meta):
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


class AdminUserSerializer(SelfUserRegistrationSerializer):
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

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class GetOrPatchUserSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class ObtainTokenSerializer(serializers.ModelSerializer):

    username = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        validate_confirmation_code(username, confirmation_code)

        return data
