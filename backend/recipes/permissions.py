from rest_framework.permissions import SAFE_METHODS


class IsAuthorOnly(BaseException):
    """Доступ к объекту только автору."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return ((request.method in SAFE_METHODS) or
                (request.method == 'POST' and request.user.is_authenticated) or
                (request.method in ['PATCH', 'DELETE'] and
                request.user.is_authenticated and
                obj.author == request.user)
                )
