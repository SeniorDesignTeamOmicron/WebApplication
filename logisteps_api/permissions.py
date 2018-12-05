from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the Location
        return obj.owner == request.user

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class UserDetailPermissions(permissions.BasePermission):
    """
    Custom permission to let anyone create a user, but
    only let user's view or edit their information
    """
    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return True
        else:
            return obj == request.user or request.user.is_superuser