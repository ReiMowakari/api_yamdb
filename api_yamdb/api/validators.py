from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from api_yamdb.settings import MAX_SCORE, MIN_SCORE
from reviews.models import CustomUser


def validate_username_allowed(username):
    """Валидатор проверяет предоставленный username на допустимость."""
    if username in settings.FORBIDDEN_USERNAMES:
        raise serializers.ValidationError(
            {
                'username': (
                    f'Использовать {username} в качестве имени'
                    ' пользователя запрещено.'
                )
            }
        )


def validate_data_unique_together(username, email):
    """
    Валидатор проверяет предоставленные данные пользователем на корректность.

    Предоставленные username и email должны совпадать в бд, или оба
    отсутствовать в бд, иначе ошибка валидации.
    """
    try:
        user = CustomUser.objects.get(username=username)
        if user.email != email:
            raise serializers.ValidationError(
                {'username': 'Никнейм занят.'}
            )
    except CustomUser.DoesNotExist:
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'Почта занята.'}
            )


def validate_confirmation_code(username, confirmation_code):
    """
    Валидатор проверяет confirmation_code юзера.

    Если код из запроса и код юзера не сопвпадают, вызывается ошибка валидации.
    Если в бд нет юзера с переданным username, вызывается ошибка
    NotFound - отсутствие объекта в бд.
    """
    try:
        user = CustomUser.objects.get(username=username)
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения.'}
            )
    except CustomUser.DoesNotExist:
        raise NotFound(
            {'username': 'Такого пользователя не существует.'}
        )


def validate_score(value):
    """
    Валидатор для проверки оценки отзыва от 1 до 10, включительно.
    :param value: принимает на вход значение Score из сериализатора.
    :return: возвращает Score или же 400 ошибку.
    """
    if MIN_SCORE < value < MAX_SCORE:
        return value
    raise serializers.ValidationError(
        'Оценка должна быть в диапазоне от 1 до 10 влючительно.')
