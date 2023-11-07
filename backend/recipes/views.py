from collections import defaultdict
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import (
    FAVORITES_DELETE_MESSAGE, FAVORITES_EXISTS_MESSAGE,
    NOT_IN_FAVORITES_MESSAGE, NOT_IN_SHOP_CART_MESSAGE,
    RECIPE_DOES_NOT_EXIST, SHOP_CART_DELETE_MESSAGE, SHOP_CART_EXISTS_MESSAGE
)
from .filters import RecipeFilter
from .models import Favorites, Ingredient, Recipe, ShoppingCart, Tag
from .mixins import CreateDestroyListMixin
from .pagination import RecipesPagination
from .permissions import (
    CustomRecipePermission, IsAdminOrReadOnly, IsAuthorOnly
)
from .serializers import (
    FavoritesSerializer, IngredientSerializer,
    RecipeSerializer, ShoppingCartSerializer, TagSerializer
)


class FavoritesViewSet(CreateDestroyListMixin):
    """Вьюсет для создания, удаления и отображения избранного"""
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoritesSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user

        try:
            Recipe.objects.get(id=self.kwargs.get('recipe_id'))
        except Recipe.DoesNotExist:
            return Response(
                RECIPE_DOES_NOT_EXIST,
                status=status.HTTP_400_BAD_REQUEST
                )

        recipe = Recipe.objects.get(id=self.kwargs.get('recipe_id'))
        if not Favorites.objects.filter(recipe=recipe, user=user):
            favorites = Favorites.objects.create(recipe=recipe, user=user)
            serializer = self.get_serializer(favorites)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(
            FAVORITES_EXISTS_MESSAGE, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        recipe = self.get_recipe()
        user = request.user

        try:
            favorite = Favorites.objects.get(recipe=recipe, user=user)
            favorite.delete()
            return Response(
                FAVORITES_DELETE_MESSAGE, status=status.HTTP_204_NO_CONTENT
                )
        except Favorites.DoesNotExist:
            return Response(
                NOT_IN_FAVORITES_MESSAGE, status=status.HTTP_404_NOT_FOUND
                )

    def get_queryset(self):
        return Favorites.objects.filter(user=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюест для ингредиентов"""
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    search_fields = ('^name')


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами"""
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    pagination_class = RecipesPagination
    permission_classes = (CustomRecipePermission,)
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()


class ShoppingCartViewSet(CreateDestroyListMixin):
    """
    Вьюсет для добавления и удаления рецептов и отображения списка
    покупок.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ShoppingCartSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user

        try:
            Recipe.objects.get(id=self.kwargs.get('recipe_id'))
        except Recipe.DoesNotExist:
            return Response(
                RECIPE_DOES_NOT_EXIST,
                status=status.HTTP_400_BAD_REQUEST
                )

        recipe = Recipe.objects.get(id=self.kwargs.get('recipe_id'))
        if not ShoppingCart.objects.filter(recipe=recipe, user=user):
            shopping_cart = ShoppingCart.objects.create(
                recipe=recipe, user=user
                )
            serializer = self.get_serializer(shopping_cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            SHOP_CART_EXISTS_MESSAGE, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        recipe = self.get_recipe()
        user = request.user
        try:
            recipe = ShoppingCart.objects.get(recipe=recipe, user=user)
            recipe.delete()
            return Response(
                SHOP_CART_DELETE_MESSAGE, status=status.HTTP_204_NO_CONTENT
                )
        except ShoppingCart.DoesNotExist:
            return Response(
                NOT_IN_SHOP_CART_MESSAGE, status=status.HTTP_400_BAD_REQUEST
                )

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)


class ShoppingCartDownLoadView(APIView):
    """
    Класс для загрузки списка покупок с суммированием повторяющихся
      ингредиентов.
    """
    permission_classes = (IsAuthorOnly,)
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()

    def get(self, request):
        shopping_cart_dict = defaultdict(
            lambda: {'amount': 0, 'measurement_unit': ''}
            )
        user = self.request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)

        for ingredients in shopping_cart:
            for ingredient in ingredients.recipe.ingredients_used.all():
                amount = ingredient.amount
                measurement_unit = ingredient.ingredient.measurement_unit
                ingredient_key = ingredient.ingredient.name
                shopping_cart_dict[ingredient_key]['amount'] += amount
                shopping_cart_dict[ingredient_key]['measurement_unit'] = (
                    measurement_unit
                )
        shopping_list = "\n".join(
            [f"{ingredient} {data['amount']} {data['measurement_unit']}"
             for ingredient, data in shopping_cart_dict.items()]
            )

        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
