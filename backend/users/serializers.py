from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .constants import USERNAME_ERROR_MESSAGE, USERNAME_REQUIRED_ERROR
from .models import BlacklistedToken, User


class BlacklistedTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlacklistedToken
        fields = ('token',)


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователей"""
    username = serializers.RegexField(
        regex=r'^[a-zA-Z0-9]+$',
        max_length=150,
        required=True,
        error_messages={
            'invalid': USERNAME_ERROR_MESSAGE,
            'required': USERNAME_REQUIRED_ERROR,
        }
    )
    email = serializers.EmailField(max_length=250, required=True)

    class Meta:
        fields = ('username', 'name', 'last_name', 'email', 'password', )
        model = User

    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError(USERNAME_REQUIRED_ERROR)
        elif len(value) < 6:
            raise ValidationError(
                'Логин слишком короткий. Минимальная длина: 6 символа.'
            )
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class TokenSerializer(serializers.ModelSerializer):
    '''Сериализатор получения токена пользователя'''
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'password')


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя для запроса /users/me/"""

    class Meta:
        fields = ('username', 'email', 'name', 'last_name',)
        model = User


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор пользователя'''
    class Meta:
        fields = '__all__'
        model = User

