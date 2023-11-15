import webcolors
from django.core.validators import MaxValueValidator, MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import UserSerializer
from .constants import (INGREDIENTS_MIN_VALUE, POSITIVE_SMALL_MAX,
                        TIME_MIN_VALUE)
from .models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


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
    """Сериализатор ингредиентов."""

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели рецептов и ингредиентов."""

    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )

    class Meta:
        fields = ('id', 'amount', 'measurement_unit', 'name')
        model = RecipeIngredient


class AmountIngredientSerializer(serializers.ModelSerializer):
    """Промежуточный сериализатор количества ингредиентов в рецепте для POST
    запросов.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(
                INGREDIENTS_MIN_VALUE,
                message=(
                    'Количество ингрендиентов не должно быть меньше {0}. '
                    'Введите допустимое значение'.format(INGREDIENTS_MIN_VALUE)
                ),
            ),
            MaxValueValidator(
                POSITIVE_SMALL_MAX,
                message=(
                    'Количество ингрендиентов не должно быть больше {0}. '
                    'Введите допустимое значение'.format(POSITIVE_SMALL_MAX)
                ),
            ),
        ],
    )

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


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

    class Meta:
        fields = (
            'id', 'author', 'name', 'text', 'image', 'ingredients', 'tags',
            'cooking_time'
        )
        model = Recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('request') == 'GET':
            representation['is_favorited'] = instance.is_favorited
            representation['is_in_shopping_cart'] = (
                instance.is_in_shopping_cart
            )
        return representation


class RecipeCreateUpdateSerializer(RecipeSerializer):
    """Сериализатор рецептов для POST запросов."""

    EMPTY_INGREDIENTS_ERROR = {'detail': 'Отсутствуют ингредиенты'}
    EMPTY_IMAGE_ERROR = {'detail': 'Отсутствует изображение'}
    EMPTY_TAGS_ERROR = {'detail': 'Отсутствуют теги'}
    DOUBLE_INGREDIENT_ERROR = {'detail': 'Повтор ингредиентов'}
    DOUBLE_TAG_ERROR = {'detail': 'Повтор тегов'}
    RECIPE_ALREADY_EXISTS_ERROR = {'detail': "Рецепт уже был добавлен"}

    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(TIME_MIN_VALUE),
            MaxValueValidator(POSITIVE_SMALL_MAX),
        ],

    )
    author = UserSerializer(default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True)
    ingredients = AmountIngredientSerializer(many=True)
    is_favorited = serializers.ReadOnlyField(read_only=True, default=False)
    is_in_shopping_cart = serializers.ReadOnlyField(
        read_only=True, default=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        allow_empty=False,
    )

    class Meta:
        fields = RecipeSerializer.Meta.fields + ('is_favorited',
                                                 'is_in_shopping_cart')
        model = Recipe

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise ValidationError(self.EMPTY_INGREDIENTS_ERROR)
        ingredients_list = [
            ingredient['id'] for ingredient in ingredients
        ]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise ValidationError(self.DOUBLE_INGREDIENT_ERROR)

        text = data.get('text')
        if Recipe.objects.filter(text=text):
            raise ValidationError(self.RECIPE_ALREADY_EXISTS_ERROR)

        return data

    def validate_image(self, image):
        if not image:
            raise ValidationError(self.EMPTY_IMAGE_ERROR)

        return image

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError(self.EMPTY_TAGS_ERROR)

        if len(tags) != len(set(tags)):
            raise ValidationError(self.DOUBLE_TAG_ERROR)

        return tags

    @staticmethod
    def ingredients_create_update_data_iteration(recipe_id, ingredients_data):
        recipe_ingredients = [
            RecipeIngredient(
                recipe_id=recipe_id,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount'])
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        author = validated_data.pop('author')
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.ingredients_create_update_data_iteration(
            recipe_id=recipe.id,
            ingredients_data=ingredients_data
        )

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        instance.ingredients.clear()
        self.ingredients_create_update_data_iteration(
            recipe_id=instance.id,
            ingredients_data=ingredients_data
        )

        instance.tags.clear()
        instance.tags.set(tags_data)

        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        data = RecipeSerializer(
            instance, context={'request': self.context.get('request')}
        ).data
        data['is_favorited'] = False
        data['is_in_shopping_cart'] = False
        return data


class ShortRecipeSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class FavShopSerializer(serializers.ModelSerializer):
    """Родительский сериализатор для избранного и списка покупок."""

    ALREADY_EXIST_ERROR = {'detail': 'Рецепт уже находится в списке'}

    def validate(self, data):
        model = getattr(self.Meta, 'model', None)
        if model:
            if model.objects.filter(**data).exists():
                raise ValidationError(self.ALREADY_EXIST_ERROR)
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class FavoritesSerializer(FavShopSerializer):
    """Сериализатор избранного."""

    class Meta:
        fields = ('recipe', 'user')
        model = Favorites


class ShoppingCartSerializer(FavShopSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        fields = ('recipe', 'user')
        model = ShoppingCart
