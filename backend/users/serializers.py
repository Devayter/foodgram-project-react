from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Recipe

from .models import Subscribe, User


class UserSerializer(UserSerializer):
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
                and obj.author.author.filter(subscriber=request.user).exists())

    # return (request
    #             and request.user.is_authenticated
    #             and obj.author.author.filter(
    # subscriber=request.user).exists())


class ShortRecipeSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscribeSerializer(UserSerializer):
    """Сериализатор подписок для GET запросов."""

    recipes = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    email = serializers.ReadOnlyField(source='author.email')
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'recipes_count', 'recipes', 'is_subscribed'
        )
        model = User

    def get_recipes(self, instance):
        print('>>>', type(instance))
        recipes = Recipe.objects.filter(author=instance.author)
        if self.context:
            recipes_limit = self.context['request'].query_params.get(
                'limit'
            )
            if recipes_limit and recipes_limit.isdigit():
                recipes = recipes[:int(recipes_limit)]

        return ShortRecipeSerializer(
            recipes, context=self.context,
            many=True
        ).data


class SubscribeCreateDeleteSerializer(SubscribeSerializer):
    """Сериализатор для создания и удаления подписок."""

    SELF_SUBSCRIPTION_ERROR = {
        'detail': 'Невозвожно подписаться на самого себя'
    }
    SUBSCRIPTION_ALREADY_EXISTS = {
        'detail': 'Вы уже подписаны на этого пользователя'
    }

    class Meta:
        fields = SubscribeSerializer.Meta.fields + ('author', 'subscriber')
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

    # def to_representation(self, instance):
    #     print('><<>>>', instance)
    #     return SubscribeSerializer(instance.author).data
