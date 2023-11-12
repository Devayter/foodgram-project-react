from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet,
                    ShoppingCartDownLoadView, TagViewSet)

app_name = 'recipes'

router_v1 = DefaultRouter()

router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartDownLoadView.as_view(),
        name='download_shopping_cart'
    ),
    path('', include(router_v1.urls))
]
