from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .validators import (
    validate_username_allowed,
    validate_data_unique_together,
    validate_confirmation_code
)
from reviews.models import CustomUser, Group


class SelfUserRegistrationSerializer(serializers.ModelSerializer):

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

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
        required=True
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
        required=True
    )

    role = serializers.SlugRelatedField(
        slug_field='name', queryset=Group.objects.all()
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


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
