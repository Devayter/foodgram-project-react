from rest_framework.permissions import SAFE_METHODS


class Base(BaseException):
    """Доступ к объекту только автору."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.method == 'POST'

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or request.method == 'POST'
