import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .constants import RECIPE_ALREADY_EXISTS_ERROR
from .models import (
    Favorites, Follow, Ingredient, Recipe, RecipeIngredient,
    RecipeTag, ShoppingCart, Tag, User
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
        slug_field='username'
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        read_only=False,
        slug_field='username'
    )
    validators = [
        UniqueTogetherValidator(
            queryset=Favorites.objects.all(),
            fields=('recipe', 'following')
        )
    ]

    class Meta:
        fields = ('user', 'following')
        model = Follow


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(),
    measurement = serializers.StringRelatedField(
        source='ingredient.measurement',
        )
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = RecipeIngredient
        read_only_fields = ('measurement',)


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        fields = '__all__'
        model = Tag


class RecipeTagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = RecipeTag


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
        slug_field='username'
    )
    image = Base64ImageField(required=False)
    ingredients = RecipeIngredientSerializer(
        source='ingredients_used',
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        allow_empty=False,
    )

    class Meta:
        fields = '__all__'
        model = Recipe

    def create(self, validated_data):
        description = validated_data['description']
        ingredients_data = validated_data.pop('ingredients_used')
        tags_data = validated_data.pop('tags')
        if Recipe.objects.filter(description=description):
            raise serializers.ValidationError(RECIPE_ALREADY_EXISTS_ERROR)
        recipe = Recipe.objects.create(**validated_data)
        recipe_id = recipe.id
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe_id=recipe_id,
                **ingredient_data)
        recipe.tags.set(tags_data)
        return recipe


class FavoritesSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer()
    user = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
        slug_field='username'
    )
    validators = [
        UniqueTogetherValidator(
            queryset=Favorites.objects.all(),
            fields=('recipe', 'user')
        )
    ]

    class Meta:
        fields = '__all__'
        model = Favorites
        read_only_fields = ('recipe',)


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer()
    user = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
        slug_field='username'
    )

    validators = [
        UniqueTogetherValidator(
            queryset=Favorites.objects.all(),
            fields=('recipe', 'user')
        )
    ]

    class Meta:
        fields = '__all__'
        model = ShoppingCart
        read_only_fields = ('recipe',)
