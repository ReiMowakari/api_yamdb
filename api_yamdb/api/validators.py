from django.conf import settings
from rest_framework import serializers

from reviews.models import CustomUser


def validate_username_allowed(username):
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
    try:
        user = CustomUser.objects.get(username=username)
        #  TODO Добавить проверку, что confirmation_code уже был получен?
        #  То есть, есть ли значение в бд. Вроде не требуется по тз.
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения.'}
            )
    except CustomUser.DoesNotExist:
        raise serializers.ValidationError(
            {'username': 'Такого пользователя не существует.'}
        )
