from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User
from .constants import (INGREDIENTS_MIN_VALUE, NAME_SLUG_MEASURE_MAX_LENGTH,
                        POSITIVE_SMALL_MAX, TIME_MIN_VALUE)


class RecipeUser(models.Model):
    """Абстрактная родительская модель для списка покупок и избранного."""

    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Пользователь'
    )

    class Meta:
        abstract = True
        verbose_name = 'Список покупок и избранного'

    def __str__(self):
        return f'{self.recipe}, {self.user}'


class Favorites(RecipeUser):
    """Модель избранного."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_recipe_user'
            )
        ]
        verbose_name = 'Избранное'


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        max_length=NAME_SLUG_MEASURE_MAX_LENGTH,
        verbose_name='Наименование ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=NAME_SLUG_MEASURE_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                TIME_MIN_VALUE,
                message=('Время готовки не должно быть  равно нулю.'),
            ),
            MaxValueValidator(
                POSITIVE_SMALL_MAX,
                message=(
                    '{POSITIVE_SMALL_MAX} - максимальное допустимое значение.'
                ),
            ),
        ],
        verbose_name='Время приготовления (мин.)'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    image = models.ImageField(
        upload_to='images',
        verbose_name='Фото блюда'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    name = models.CharField(
        max_length=NAME_SLUG_MEASURE_MAX_LENGTH,
        verbose_name='Название рецепта'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    tags = models.ManyToManyField(
        'Tag',
        through='RecipeTag',
        verbose_name='Тэг'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} {self.text}'


class RecipeIngredient(models.Model):
    """Промежуточная таблица ингредиентов для рецепта."""

    amount = models.PositiveSmallIntegerField(
        null=False,
        validators=[
            MinValueValidator(
                INGREDIENTS_MIN_VALUE,
                message=('Количество ингрендиентов не должно быть равно нулю'),
            ),
            MaxValueValidator(
                POSITIVE_SMALL_MAX,
                message=(
                    f'{POSITIVE_SMALL_MAX} - максимальное допустимое значение.'
                ),
            ),
        ],
        verbose_name='Количество'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_used',
        verbose_name='Ингредиенты в рецепте'
    )

    class Meta:
        verbose_name = 'Рецепт и Ингредиент'
        verbose_name_plural = 'Рецепты и Ингредиенты'

    def __str__(self):
        return (
            f'{self.amount} {self.ingredient.measurement_unit} '
            f'{self.ingredient}'
        )


class RecipeTag(models.Model):
    """Промежуточная модель тегов для рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE,
        verbose_name='Тэг'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tag'
            )
        ]
        verbose_name = 'Рецепт и Тэг'
        verbose_name_plural = 'Рецепты и Тэги'

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class ShoppingCart(RecipeUser):
    """Модель списка покупок."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_shoping_cart_recipe_user'
            )
        ]
        verbose_name = 'Список покупок'


class Tag(models.Model):
    """Модель тегов."""

    color = ColorField(unique=True, verbose_name='Цветовое обозначение тэга')
    name = models.CharField(
        max_length=NAME_SLUG_MEASURE_MAX_LENGTH,
        unique=True,
        verbose_name='Имя тэга'
    )
    slug = models.SlugField(
        max_length=NAME_SLUG_MEASURE_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг тэга'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name
