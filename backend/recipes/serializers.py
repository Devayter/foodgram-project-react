import webcolors
from django.core.validators import MaxValueValidator, MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import UserSerializer

from .constants import MAX_VALUE_180, MIN_VALUE_1
from .models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag, User)

# import base64




class Hex2NameColor(serializers.Field):
    """Сериализатор цветового кода."""

    NO_COLOR_NAME_ERROR = 'Для этого цвета нет имени'

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise ValidationError(self.NO_COLOR_NAME_ERROR)
        return data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели рецептов и ингредиентов."""
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_VALUE_1)
        ]
    )
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
        read_only_fields = ('measurement_unit', 'name', 'id')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    color = Hex2NameColor()

    class Meta:
        fields = '__all__'
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов для GET запросов."""

    EMPTY_INGREDIENTS_ERROR = 'Отсутствуют ингредиенты'
    EMPTY_TAGS_ERROR = 'Отсутствуют теги'

    ingredients = RecipeIngredientSerializer(
        source='ingredients_used',
        many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'author', 'name', 'text', 'image', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'tags', 'cooking_time'
        )
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated and
            Favorites.objects.filter(recipe=obj, user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated and
            ShoppingCart.objects.filter(recipe=obj, user=request.user).exists()
        )

    def to_representation(self, instance):
        data = super(RecipeSerializer, self).to_representation(instance)
        data['author'] = UserSerializer(instance.author).data
        data['tags'] = TagSerializer(instance.tags, many=True).data
        return data


class RecipeCreateUpdateSerializer(RecipeSerializer):
    """Сериализатор рецептов для POST запросов."""

    EMPTY_INGREDIENTS_ERROR = {'detail': 'Отсутствуют ингредиенты'}
    EMPTY_TAGS_ERROR = {'detail': 'Отсутствуют теги'}
    DOUBLE_INGREDIENT_ERROR = {'detail': 'Повтор ингредиентов'}
    DOUBLE_TAG_ERROR = {'detail': 'Повтор тегов'}
    RECIPE_ALREADY_EXISTS_ERROR = {'detail': "Рецепт уже был добавлен"}

    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_VALUE_1),
            MaxValueValidator(MAX_VALUE_180),
        ],

    )
    author = UserSerializer(default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True)
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
        fields = (
            'id', 'author', 'name', 'text', 'image', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'tags', 'cooking_time'
        )
        model = Recipe

    def validate(self, data):
        ingredients = data.get('ingredients_used')
        if not ingredients:
            raise ValidationError(self.EMPTY_INGREDIENTS_ERROR)

        ingredients_list = [
            ingredient['ingredient'] for ingredient in ingredients
        ]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise ValidationError(self.DOUBLE_INGREDIENT_ERROR)

        text = data.get('text')
        if Recipe.objects.filter(text=text):
            raise ValidationError(self.RECIPE_ALREADY_EXISTS_ERROR)

        return data

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError(self.EMPTY_TAGS_ERROR)

        if len(tags) != len(set(tags)):
            raise ValidationError(self.DOUBLE_TAG_ERROR)

        return tags

    @staticmethod
    def ingredients_create_update_data_iteration(recipe_id, ingredients_data):
        recipe_ingredients = [
            RecipeIngredient(recipe_id=recipe_id, **ingredient_data)
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients_used')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe_id = recipe.id
        self.ingredients_create_update_data_iteration(
            recipe_id=recipe_id,
            ingredients_data=ingredients_data
        )

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients_used')
        tags_data = validated_data.pop('tags')
        super().update(instance, validated_data)

        instance.ingredients.clear()
        self.ingredients_create_update_data_iteration(
            recipe_id=instance.id,
            ingredients_data=ingredients_data
        )

        self.validate_tags(tags_data)
        instance.tags.clear()
        for tag_data in tags_data:
            RecipeTag.objects.get_or_create(
                recipe_id=instance.id, tag=tag_data
            )

        instance.save()
        return instance


class FavShopSerializer(serializers.ModelSerializer):
    """Родительский сериализатор для избранного и списка покупок."""

    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )
    image = serializers.ImageField(source='recipe.image', read_only=True)

    validators = [
        UniqueTogetherValidator(
            queryset=ShoppingCart.objects.all(),
            fields=('recipe', 'user')
        )
    ]

    class Meta:
        fields = '__all__'
        model = Recipe

    def validate(self, data):
        if self.Meta:
            return data
        raise ValidationError('Какая-то ошибка')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['name'] = instance.recipe.name
        data['cooking_time'] = instance.recipe.cooking_time
        return data


class FavoritesSerializer(FavShopSerializer):
    """Сериализатор избранного."""

    class Meta:
        fields = '__all__'
        model = Favorites


class ShoppingCartSerializer(FavShopSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        fields = '__all__'
        model = ShoppingCart
