from django.contrib import admin

from .models import (
    Favorites, Ingredient, Recipe, RecipeIngredient, RecipeTag, ShoppingCart,
    Tag
)

admin.site.register(Favorites)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
