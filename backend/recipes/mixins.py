from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets

from .models import Recipe


class CreateDestroyListMixin(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Базовый класс для FavoritesViewSet и ShoppingCartViewSet"""

    def get_recipe(self):
        return get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
