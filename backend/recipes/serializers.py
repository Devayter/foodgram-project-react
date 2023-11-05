import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .constants import RECIPE_ALREADY_EXISTS_ERROR
from .models import (
    Favorites, Ingredient, Recipe, RecipeIngredient,
    RecipeTag, ShoppingCart, Tag, User
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        )
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        fields = ('id', 'amount', 'measurement_unit', 'name')
        model = RecipeIngredient
        read_only_fields = ('measurement_unit', 'name')


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        fields = '__all__'
        model = Tag


class RecipeTagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = RecipeTag


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',)


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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        allow_empty=False,
    )

    class Meta:
        fields = '__all__'
        model = Recipe

    def get_is_favorited(self, obj):
        if self.context.get('request').user.is_authenticated:
            user = self.context.get('request').user
            recipe = obj
            return Favorites.objects.filter(recipe=recipe, user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.is_authenticated:
            user = self.context.get('request').user
            recipe = obj
            return Favorites.objects.filter(recipe=recipe, user=user).exists()
        return False

    def create(self, validated_data):
        text = validated_data['text']
        ingredients_data = validated_data.pop('ingredients_used')
        tags_data = validated_data.pop('tags')
        if Recipe.objects.filter(text=text):
            raise serializers.ValidationError(RECIPE_ALREADY_EXISTS_ERROR)
        recipe = Recipe.objects.create(**validated_data)
        recipe_id = recipe.id
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe_id=recipe_id,
                **ingredient_data)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
            )
        instance.image = validated_data.get('image', instance.image)

        instance.ingredients.clear()
        ingredients_data = validated_data.get('ingredients_used')
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.get_or_create(
                recipe_id=instance.id, **ingredient_data
                )

        instance.tags.clear()
        tags_data = validated_data.get('tags')
        for tag_data in tags_data:
            RecipeTag.objects.get_or_create(
                recipe_id=instance.id, tag=tag_data
                )

        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['author'] = UserSerializer(instance.author).data
        ret['tags'] = TagSerializer(instance.tags, many=True).data

        return ret


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
