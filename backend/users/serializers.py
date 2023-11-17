from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer as DjoserSerializer
from rest_framework import serializers

from recipes.models import Recipe
from .models import Subscribe, User


class UserSerializer(DjoserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_subscribed'
        )
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and request.user.author.filter(
                    subscriber=request.user
                ).exists())


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Короткий сериализатор рецептов для подписок."""

    image = serializers.ImageField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscribeSerializer(UserSerializer):
    """Сериализатор подписок для GET запросов."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
        model = User

    def get_recipes(self, instance):
        recipes = instance.recipes.all()
        if self.context:
            recipes_limit = self.context['request'].query_params.get('limit')
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                recipes = recipes
        return ShortRecipeSerializer(
            recipes, context=self.context,
            many=True
        ).data


class SubscribeCreateDeleteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и удаления подписок."""

    SELF_SUBSCRIPTION_ERROR = {
        'detail': 'Невозвожно подписаться на самого себя'
    }
    SUBSCRIPTION_ALREADY_EXISTS = {
        'detail': 'Вы уже подписаны на этого пользователя'
    }

    class Meta:
        fields = ('author', 'subscriber')
        model = Subscribe

    def validate(self, data):
        author = data.get('author')
        subscriber = self.context['request'].user
        if author == subscriber:
            raise ValidationError(self.SELF_SUBSCRIPTION_ERROR)
        if Subscribe.objects.filter(
            author=author, subscriber=subscriber
        ).exists():
            raise ValidationError(self.SUBSCRIPTION_ALREADY_EXISTS)
        return data

    def to_representation(self, instance):
        return SubscribeSerializer(
            instance.author,
            context=self.context
        ).data
