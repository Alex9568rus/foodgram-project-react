from rest_framework.permissions import SAFE_METHODS, BasePermission


class ListOrCriatePermission(BasePermission):

    def has_permission(self, request, view):
        if view.action in ['list', 'create']:
            return True
        return request.user.is_authenticated


class IsAuthorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user is obj.author
            or request.method in SAFE_METHODS
        )


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_staff
        )
