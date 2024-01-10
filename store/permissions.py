from rest_framework import permissions


class IsOwnerOrReadonly(permissions.BasePermission): 
    """
    Permission for MobileCommentsViewSet.
    """     
    def has_object_permission(self, request, view, obj):
            return bool(obj.owner == request.user)