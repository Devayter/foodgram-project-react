from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe
from .models import Subscribe, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя для запроса /users/me/"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_subscribed'
        )
        model = User

    def get_is_subscribed(self, obj):

        return (self.context.get('request')
                and self.context.get('request').user.is_authenticated
                and Subscribe.objects.select_related('author').filter(
                    author=obj,
                    subscriber=self.context.get('request').user
                    ).exists()
                )


class SubscribeSerializer(UserSerializer):
    """Сериализатор подписок"""
    # recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    # validators = [
    #     UniqueTogetherValidator(
    #         queryset=Subscribe.objects.all(),
    #         fields=('author', 'subscriber',)
    #     )
    # ]

    class Meta:
        fields = (
            'id',
        )
        model = User


    # def to_representation(self, instance):
    #     data = super(SubscribeSerializer, self).to_representation(instance)
    #     user_id = instance.user.id
    #     recipes_limit = self.context['request'].query_params.get(
    #         'recipes_limit'
    #     )

    #     recipes = Recipe.objects.filter(author_id=user_id)
    #     if recipes_limit:
    #         recipes = recipes[:int(recipes_limit)]

    #     recipes = recipes.values('id', 'name', 'image', 'cooking_time')
    #     data['recipes'] = recipes
    #     return data
