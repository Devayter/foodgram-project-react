from rest_framework.pagination import LimitOffsetPagination


class UsersPagination(LimitOffsetPagination):
    """Пагинатор для пользователей"""
    default_limit = 10
    max_limit = 30
