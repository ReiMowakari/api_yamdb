import uuid
from smtplib import SMTPException

from rest_framework_simplejwt.tokens import AccessToken
from django.core.mail import send_mail
from django.conf import settings


def generate_and_send_code(user):
    """Отправляет код подтверждения регистрации на почту пользователю."""
    user.confirmation_code = str(uuid.uuid4())
    user.save()
    try:
        send_mail(
            subject='Код подтверждения.',
            message=f'Ваш код подтверждения:{user.confirmation_code}',
            from_email=settings.MAIL_SEND_FROM,
            recipient_list=[f'{user.email}'],
            fail_silently=False,
        )
    except SMTPException as error:
        raise error


def generate_user_token(user):
    '''Создает access- jwt токен для пользователя.'''
    access = AccessToken.for_user(user)
    return {
        'access': str(access),
    }
