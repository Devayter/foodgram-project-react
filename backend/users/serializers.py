from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.serializers import RecipeSerializer
from .constants import (
    CURRENT_PASSWORD_ERROR, USERNAME_ERROR_MESSAGE, USERNAME_REQUIRED_ERROR
)
from .models import BlacklistedToken, User, Subscribe


class BlacklistedTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlacklistedToken
        fields = ('token',)


class SetPasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data['current_password']):
            raise ValidationError(CURRENT_PASSWORD_ERROR)
        return data


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователей"""
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
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

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError(USERNAME_REQUIRED_ERROR)
        elif len(value) < 4:
            raise ValidationError(
                'Логин слишком короткий. Минимальная длина: 4 символа.'
            )
        return value


class SubscribeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
        slug_field='username'
    )
    subscriber = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        read_only=False,
        slug_field='username'
    )
    validators = [
        UniqueTogetherValidator(
            queryset=Subscribe.objects.all(),
            fields=('user', 'subscriber')
        )
    ]

    class Meta:
        fields = ('user', 'subscriber',)
        model = Subscribe

    def to_representation(self, instance):
        data = super(SubscribeSerializer, self).to_representation(instance)
        data['recipes'] = RecipeSerializer(
            instance.user.recipes, many=True
            ).data
        return data


class TokenSerializer(serializers.ModelSerializer):
    '''Сериализатор получения токена пользователя'''
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'password')


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

