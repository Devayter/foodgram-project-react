from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_SIZE


class RecipesUsersPagination(PageNumberPagination):
    """Пагинатор для рецептов."""

    page_size = PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = PAGE_SIZE
