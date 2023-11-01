from rest_framework import viewsets

from .models import (
    Favorites, Follow, Ingredient, Recipe, ShoppingCart, Tag
)
from .mixins import CreateDestroyListMixin
from .serializers import (
    FavoritesSerializer, FollowSerializer, IngredientSerializer,
    RecipeSerializer, ShoppingCartSerializer, TagSerializer
)


class FavoritesViewSet(CreateDestroyListMixin):
    serializer_class = FavoritesSerializer

    def get_queryset(self):
        return Favorites.objects.filter(user=self.request.user)


class FollowViewSet(CreateDestroyListMixin):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return Follow.objects.select_related.all().filter(
            user=self.request.user
        )


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()


class ShoppingCartViewSet(CreateDestroyListMixin):
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
