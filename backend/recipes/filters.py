from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Фильтр для поиска ингредиентов по наименования"""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов по автору, тегам, избранныи и списку покупок"""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        return queryset.filter(favorites__user=self.request.user.id)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return queryset.filter(shoppingcart__user=self.request.user.id)

    class Meta:
        model = Recipe
        fields = ('author', 'tags__slug', 'is_favorited')
