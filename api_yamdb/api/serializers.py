from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .validators import (
    validate_username_allowed,
    validate_data_unique_together,
    validate_confirmation_code
)
from reviews.models import CustomUser


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
        required=True
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
        required=True
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
