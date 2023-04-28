from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReviewOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return request.user.is_authenticated and (request.user == obj.reviewer or request.user.is_staff)
        return True