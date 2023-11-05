from rest_framework.pagination import LimitOffsetPagination


class RecipesPagination(LimitOffsetPagination):
    default_limit = 6
    max_limit = 18
