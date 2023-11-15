from django.db.models import F, Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .pagination import RecipesUsersPagination
from .permissions import IsAuthorOnly
from .serializers import (FavoritesSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюест для ингредиентов."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    RECIPE_DELETE_MESSAGE = {'detail': 'Рецепт удален из списка'}
    NOT_IN_LIST_MESSAGE = {'detail': 'Рецепт не находится в списке'}

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    pagination_class = RecipesUsersPagination
    permission_classes = (IsAuthorOnly,)
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags',
        'ingredients'
    ).all()

    def get_serializer_class(self):
        """Возвращает необходимый сериализатор."""

        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateUpdateSerializer

    @staticmethod
    def create_fav_shop(serializer, request, pk):
        """
        Статистический метод для записи в модели избранного и списка покупок.
        """

        data_dict = {'user': request.user.id, 'recipe': pk}
        serializer = serializer(data=data_dict, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_fav_shop(model, request, pk):
        """
        Статистическмй метод для удаления объектов моделей избранного и списка
        покупок.
        """

        if model.objects.filter(recipe=pk, user=request.user).exists():
            model.objects.filter(recipe=pk, user=request.user).delete()
            return Response(
                RecipeViewSet.RECIPE_DELETE_MESSAGE,
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            RecipeViewSet.NOT_IN_LIST_MESSAGE,
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=['get'],
            serializer_class=ShoppingCartSerializer)
    def download_shopping_cart(self, request):

        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit')
        ).order_by('name').annotate(total=Sum('amount'))

        shopping_list = '\n'.join(
            [f"{ingredient['name']} {ingredient['total']} {ingredient['unit']}"
             for ingredient in ingredients]
        )

        response = FileResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="Список покупок.txt"'
        )
        return response

    @action(detail=True, methods=['post', 'patch'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.create_fav_shop(FavoritesSerializer, request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_fav_shop(model=Favorites, request=request, pk=pk)

    @action(detail=True, methods=['post', 'putch'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.create_fav_shop(ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_fav_shop(ShoppingCart, request, pk)


class ShoppingCartDownLoadView(APIView):
    """
    Класс для загрузки списка покупок с суммированием повторяющихся
      ингредиентов.
    """

    # permission_classes = (IsAuthorOnly,)
    # serializer_class = ShoppingCartSerializer
    # queryset = ShoppingCart.objects.all()

    # def get(self, request):

    #     ingredients = RecipeIngredient.objects.filter(
    #         recipe__shoppingcart__user=request.user
    #     ).values(
    #         name=F('ingredient__name'),
    #         unit=F('ingredient__measurement_unit')
    #     ).order_by('name').annotate(total=Sum('amount'))

    #     return RecipeViewSet.download_shopping_list(ingredients)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
