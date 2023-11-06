from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .constants import RECIPE_DOES_NOT_EXIST
from .models import Recipe


class CreateDestroyListMixin(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Базовый класс для FavoritesViewSet и ShoppingCartViewSet"""

    def get_recipe(self):
        try:
            return Recipe.objects.get(id=self.kwargs.get('recipe_id'))
        except Recipe.DoesNotExist:
            Response(RECIPE_DOES_NOT_EXIST, status=status.HTTP_400_BAD_REQUEST)