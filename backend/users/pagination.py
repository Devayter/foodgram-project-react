from rest_framework.pagination import LimitOffsetPagination


class UsersPagination(LimitOffsetPagination):
    page_size = 10
    max_page_size = 1000
