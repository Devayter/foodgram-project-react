from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoritesViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartDownLoadView, ShoppingCartViewSet, TagViewSet)

app_name = 'recipes'

router_v1 = DefaultRouter()

router_v1.register(r'favorites', FavoritesViewSet, basename='favorites')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoritesViewSet,
    basename='add_favorite_recipe'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='add_shopping_cart_recipe'
)
router_v1.register(
    r'shopping_cart', ShoppingCartViewSet, basename='shopping_cart'
)
router_v1.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartDownLoadView.as_view(),
        name='download_shopping_cart'
    ),
    path('', include(router_v1.urls))
]
