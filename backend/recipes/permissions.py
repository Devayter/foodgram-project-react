from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import MethodNotAllowed


class IsAdminOrReadOnly(BasePermission):
    """Позволяет безопасные запросы или запросы от админа"""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or request.user.role == 'admin':
            return True
        else:
            raise MethodNotAllowed(request.method)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS or request.user.role == 'admin'
        )
