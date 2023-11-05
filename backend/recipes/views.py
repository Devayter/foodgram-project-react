from collections import defaultdict
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import (
    FAVORITES_DELETE_MESSAGE, FAVORITES_EXISTS_MESSAGE,
    NOT_IN_FAVORITES_MESSAGE, NOT_IN_SHOP_CART_MESSAGE,
    SHOP_CART_DELETE_MESSAGE, SHOP_CART_EXISTS_MESSAGE
)
from .models import Favorites, Ingredient, Recipe, ShoppingCart, Tag
from .mixins import CreateDestroyListMixin
from .permissions import IsAdminOrReadOnly
from .serializers import (
    FavoritesSerializer, IngredientSerializer,
    RecipeSerializer, ShoppingCartSerializer, TagSerializer
)


class FavoritesViewSet(CreateDestroyListMixin):
    serializer_class = FavoritesSerializer

    def create(self, request, *args, **kwargs):
        recipe = self.get_recipe()
        user = self.request.user

        if not Favorites.objects.filter(recipe=recipe, user=user):
            favorites = Favorites.objects.create(recipe=recipe, user=user)
            serializer = self.get_serializer(favorites)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        else:
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
                NOT_IN_FAVORITES_MESSAGE, status=status.HTTP_400_BAD_REQUEST
                )

    def get_queryset(self):
        return Favorites.objects.filter(user=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    search_fields = ('^name', 'name')


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()


class ShoppingCartViewSet(CreateDestroyListMixin):
    serializer_class = ShoppingCartSerializer

    def create(self, request, *args, **kwargs):
        recipe = self.get_recipe()
        user = self.request.user

        if not ShoppingCart.objects.filter(recipe=recipe, user=user):
            shopping_cart = ShoppingCart.objects.create(
                recipe=recipe, user=user
                )
            serializer = self.get_serializer(shopping_cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                SHOP_CART_EXISTS_MESSAGE, status=status.HTTP_400_BAD_REQUEST
                )

    def delete(self, request, *args, **kwargs):
        recipe = self.get_recipe()
        user = request.user

        try:
            favorite = ShoppingCart.objects.get(recipe=recipe, user=user)
            favorite.delete()
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
    '''Класс для загрузки списка покупок с суммированием повторяющихся
      ингредиентов'''
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
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
