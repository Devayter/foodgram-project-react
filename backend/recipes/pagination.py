from rest_framework.pagination import LimitOffsetPagination


class RecipesPagination(LimitOffsetPagination):
    """Пагинатор для рецептов"""

    default_limit = 6
    max_limit = 18
