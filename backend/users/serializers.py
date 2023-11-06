from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe
from .constants import (
    CURRENT_PASSWORD_ERROR, USERNAME_ERROR_MESSAGE, USERNAME_REQUIRED_ERROR,
    USERNAME_SHORT_ERROR
)
from .models import BlacklistedToken, User, Subscribe


class BlacklistedTokenSerializer(serializers.ModelSerializer):
    """Сериализатор модели черного списка токенов"""
    class Meta:
        model = BlacklistedToken
        fields = ('token',)


class SetPasswordSerializer(serializers.ModelSerializer):
    """Сериализатор смены пароля"""
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
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(max_length=250, required=True)

    class Meta:
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'password'
            )
        model = User

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError(USERNAME_REQUIRED_ERROR)
        elif len(value) < 4:
            raise ValidationError(USERNAME_SHORT_ERROR)
        return value


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор пользователя'''
    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name')
        model = User


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок"""
    username = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
        slug_field='username'
    )
    recipes_count = serializers.SerializerMethodField()
    subscriber = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        write_only=True
    )
    id = serializers.ReadOnlyField(source='user.id')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    email = serializers.ReadOnlyField(source='user.email')
    is_subscribed = serializers.SerializerMethodField()
    validators = [
        UniqueTogetherValidator(
            queryset=Subscribe.objects.all(),
            fields=('user', 'subscriber',)
        )
    ]

    class Meta:
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'subscriber',
            'is_subscribed', 'recipes_count'
            )
        model = Subscribe

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscribe.objects.filter(subscriber=user).exists()

    def get_recipes_count(self, obj):
        user_id = self.context['request'].resolver_match.kwargs.get('user_id')
        return Recipe.objects.filter(author_id=user_id).count()

    def to_representation(self, instance):
        data = super(SubscribeSerializer, self).to_representation(instance)
        user_id = instance.user.id
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
            )

        recipes = Recipe.objects.filter(author_id=user_id)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]

        recipes = recipes.values('id', 'name', 'image', 'cooking_time')
        data['recipes'] = recipes
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

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_subscribed'
                  )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscribe.objects.filter(user=user).exists()
