from django.contrib.auth.models import User
from rest_framework import permissions
from ipynbsrv.core.models import BackendUser


class IsAuthenticatedMixin(object):

    def is_authenticated(self, request):
        return request.user and request.user.is_authenticated()


class IsGroupAdminMixin(object):

    def is_group_admin(self, user, group):
        return user in group.admins


class IsPublicMixin(object):

    def is_public(self, obj):
        return obj.is_public


class IsSafeMethodMixin(object):

    def is_safe_method(self, request):
        return request.method in permissions.SAFE_METHODS


class IsBackendUserMixin(object):

    def is_backend_user(self, user):
        return hasattr(user, 'backend_user')


class IsObjectOwnerMixin(object):

    def is_owner(self, user, obj):
        if type(obj.owner) == User:
            return obj.owner == user
        elif type(obj.owner) == BackendUser:
            return obj.owner == user.backend_user


class IsObjectCreatorMixin(object):

    def is_owner(self, user, obj):
        if type(obj.creator) == User:
            return obj.creator == user
        elif type(obj.creator) == BackendUser:
            return obj.creator == user.backend_user


class IsSuperUserMixin(object):

    def is_superuser(self, user):
        return user.is_superuser


class IsAuthenticatedAndReadOnly(
        permissions.BasePermission,
        IsAuthenticatedMixin,
        IsSafeMethodMixin):

    def has_permission(self, request, view):
        if self.is_authenticated(request):
            return self.is_safe_method(request)

    def has_object_permission(self, request, view, obj):
        if self.is_authenticated(request):
            return self.is_safe_method(request)


class IsSuperUser(
        permissions.BasePermission,
        IsSuperUserMixin):

    def has_permission(self, request, view):
        return self.is_superuser(request.user)

    def has_object_permission(self, request, view, obj):
        return self.is_superuser(request.user)


class IsSuperUserOrReadOnly(
        permissions.BasePermission,
        IsSuperUserMixin,
        IsSafeMethodMixin):

    def has_object_permission(self, request, view, obj):
        if self.is_safe_method(request):
            return True
        if self.is_superuser(request.user):
            return True
        return False


class IsSuperUserOrIsObjectOwner(
        permissions.BasePermission,
        IsObjectOwnerMixin,
        IsBackendUserMixin,
        IsSuperUserMixin):
    """
    Only allow access to BackendUser which is set as owner of the object.
    """

    def has_object_permission(self, request, view, obj):
        if self.is_superuser(request.user):
            return True
        if self.is_backend_user(request.user):
            return self.is_owner(request.user, obj)
        return False


class IsSuperUserOrIsObjectOwnerOrReadOnlyIfPublic(
        IsSuperUserOrIsObjectOwner,
        IsPublicMixin,
        IsSafeMethodMixin):
    """
    Todo: write doc.
    """

    def has_object_permission(self, request, view, obj):
        if self.is_public and self.is_safe_method(request):
            return True
        if self.is_superuser(request.user):
            return True
        if self.is_backend_user(request.user):
            return self.is_owner(request.user, obj)
        return False


class IsSuperUserOrIsGroupAdminOrReadOnly(
        permissions.BasePermission,
        IsSuperUserMixin,
        IsGroupAdminMixin,
        IsSafeMethodMixin):
    """
    Todo: write doc.
    """

    def has_object_permission(self, request, view, obj):
        if self.is_safe_method(request):
            return True
        if self.is_superuser(request.user):
            return True
        if self.is_backend_user(request.user):
            return self.is_owner(request.user, obj) \
                or self.is_group_admin(request.user, obj)
        return False
