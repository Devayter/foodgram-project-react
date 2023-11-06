from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Favorites(models.Model):
    '''Модель избранного'''
    recipe = models.ForeignKey(
        'Recipe',
        blank=False,
        on_delete=models.CASCADE,
        related_name='recipe_favorites',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='user_favorites',
        verbose_name='Пользователь'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_recipe_user'
            )
        ]
        verbose_name = 'Избранное'


class Ingredient(models.Model):
    '''Модель ингредиентов'''
    name = models.CharField(
        blank=False,
        max_length=50,
        unique=True,
        verbose_name='Наименование ингредиента'
    )
    measurement_unit = models.CharField(
        blank=False,
        max_length=15,
        verbose_name='Единица измерения'
        )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''Модель рецептов'''
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    cooking_time = models.IntegerField(
        blank=False,
        verbose_name='Время приготовления (мин.)'
    )
    text = models.TextField(
        blank=False,
        verbose_name='Описание рецепта'
    )
    image = models.ImageField(
        blank=False,
        null=False,
        upload_to='recipes/images',
        verbose_name='Фото блюда')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    name = models.CharField(
        blank=False,
        max_length=200,
        verbose_name='Название рецепта')
    tags = models.ManyToManyField(
        'Tag',
        through='RecipeTag'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} {self.text}'


class RecipeIngredient(models.Model):
    '''Промежуточная таблица ингредиентов для рецепта'''
    amount = models.IntegerField(
        blank=False,
        null=False,
        verbose_name='количество'
        )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_used'
    )

    def __str__(self):
        return (
            f'{self.amount} {self.ingredient.measurement_unit}'
            '{self.ingredient}'
        )


class RecipeTag(models.Model):
    '''Промежуточная модель тегов для рецепта'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tag'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class ShoppingCart(models.Model):
    '''Модель списка покупок'''
    recipe = models.ForeignKey(
        Recipe,
        blank=False,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Список покупок'


class Tag(models.Model):
    '''Модель тегов'''
    color = models.CharField(
        blank=False,
        max_length=7,
        unique=True,
        verbose_name='Цветовое обозначение тега')
    name = models.CharField(
        blank=False,
        max_length=50,
        unique=True,
        verbose_name='Имя тега')
    slug = models.SlugField(
        blank=False,
        max_length=50,
        unique=True,
        verbose_name='Слаг тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
