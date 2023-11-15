from rest_framework.pagination import LimitOffsetPagination

from .constants import PAGE_SIZE


class RecipesUsersPagination(LimitOffsetPagination):
    """Пагинатор для рецептов."""
    default_limit = PAGE_SIZE
    page_size = PAGE_SIZE
    limit_query_param = 'limit'
