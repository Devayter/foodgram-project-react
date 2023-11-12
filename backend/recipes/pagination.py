from rest_framework.pagination import LimitOffsetPagination

from .constants import PAGE_SIZE_6


class RecipesUsersPagination(LimitOffsetPagination):
    """Пагинатор для рецептов."""
    page_size = PAGE_SIZE_6
    page_size_query_param = 'page_size'
