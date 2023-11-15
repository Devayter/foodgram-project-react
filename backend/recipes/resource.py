from import_export import resources

from .models import Ingredient


class IngredientResource(resources.ModelResource):
    """Настройка импорта для админки."""

    class Meta:
        model = Ingredient
