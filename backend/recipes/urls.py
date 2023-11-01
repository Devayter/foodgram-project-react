from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoritesViewSet, FollowViewSet, IngredientViewSet, RecipeViewSet,
    ShoppingCartViewSet, TagViewSet
)

app_name = 'recipes'

router_v1 = DefaultRouter()

router_v1.register(r'favorites', FavoritesViewSet, basename='favorites')
router_v1.register(r'follows', FollowViewSet, basename='follows')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(
    r'shoppingcart', ShoppingCartViewSet, basename='shoppingcart'
    )
router_v1.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt'))
]
