from rest_framework import permissions


class IsGroupAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        return False
        if request.method in permissions.SAFE_METHODS:
            print("safe method")
            return True
        if request.user:
            print("request user set")
            # Write permissions are only allowed to the owner of the snippet.
            ret = request.user in obj.admins
            print("ret = " + ret)
        return False


class IsBackendUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins of an object to edit it.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            print("safe method")
            return True
        if hasattr(request.user, 'backend_user'):
            return True
        return False
