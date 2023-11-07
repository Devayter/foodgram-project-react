from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag)
from .resource import IngredientResource


class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource


admin.site.register(Favorites)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
