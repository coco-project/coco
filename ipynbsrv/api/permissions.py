from rest_framework import permissions


class IsGroupAdminMixin(object):

    def is_group_admin(self, request, group):
        return request.user in group.admins


class IsSafeMethodMixin(object):

    def is_safe_method(self, request):
        return request.method in permissions.SAFE_METHODS


class IsBackendUserMixin(object):

    def is_backend_user(self, request):
        return hasattr(request.user, 'backend_user')


class IsOwnerMixin(object):

    def is_owner(self, user, obj):
        return obj.owner == user


class IsSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        print("mama mia!")
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        print("mama mia!")
        return request.user.is_superuser


class IsGroupAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            print("safe method")
            return True
        if request.user:
            print("request user set")
            # Write permissions are only allowed to the owner of the snippet.
            ret = request.user in obj.admins
            print("ret = " + ret)
            return ret
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
