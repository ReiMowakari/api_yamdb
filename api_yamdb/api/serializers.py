from django.conf import settings
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

from .validators import (
    validate_username_allowed,
    validate_data_unique_together,
    validate_confirmation_code,
    validate_score
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
        if obj.reviews.count():
            review = Review.objects.filter(title=obj).aggregate(
                rating=Avg('score')
            )
            return review.get('rating')
        return None


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        source='author.username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('id', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
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
        validate_score(int(score))
        return super().create(validated_data)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
        read_only_fields = ('id', 'author', 'pub_date')


class SelfUserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализация данных для создания нового юзера.

    Работает только с post запросами.
    """

    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=settings.USERNAME_PATTERN,
                message='Username может содержать только цифры, буквы и'
                ' знаки: ./@/+/-/_'
            ),
        ]
    )
    email = serializers.EmailField(
        required=True,
        max_length=254
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
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all()),
            RegexValidator(
                regex=settings.USERNAME_PATTERN,
                message='Username может содержать только цифры, буквы и'
                ' знаки: ./@/+/-/_'
            )
        ],
        max_length=150
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
        max_length=254
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
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all()),
            RegexValidator(
                regex=settings.USERNAME_PATTERN,
                message='Username может содержать только цифры, буквы и'
                ' знаки: ./@/+/-/_'
            )
        ],
        max_length=150
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
        required=False,
        max_length=254
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
