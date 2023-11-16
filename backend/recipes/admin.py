from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin

from .models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag)
from .resource import IngredientResource

admin.site.unregister(Group)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('recipe',)
    empty_value_display = 'пусто'


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = 'пусто'


class IngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


class TagsInLine(admin.TabularInline):
    model = RecipeTag
    min_num = 1


@admin.register(Recipe)
class RecipetAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'name', 'get_ingredients', 'cooking_time', 'pub_date',
        'favorites_count', 'image_display', 'text',
    )
    list_display_links = ('author', 'name', 'get_ingredients', 'pub_date')
    list_filter = ('author', 'name', 'pub_date')
    search_fields = ('name',)
    empty_value_display = 'пусто'
    inlines = [
        IngredientsInline,
        TagsInLine
    ]

    @admin.display(description='Добавлено в избранное')
    def favorites_count(self, obj):
        return obj.favorites.count()

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join(
            [ingredient_used.ingredient.name
             for ingredient_used in obj.ingredients_used.all()]
        )

    @admin.display(description='Изображение')
    def image_display(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('amount', 'ingredient', 'recipe')
    list_filter = ('ingredient', 'recipe')
    search_fields = ('ingredient', 'recipe')
    empty_value_display = 'пусто'


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')
    list_filter = ('recipe', 'tag')
    search_fields = ('recipe', 'tag')
    empty_value_display = 'пусто'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('recipe',)
    empty_value_display = 'пусто'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('color', 'name', 'slug')
    list_filter = ('color', 'name', 'slug')
    search_fields = ('name', 'slug')
    empty_value_display = 'пусто'
