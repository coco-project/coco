from django.contrib.auth.models import User
from ipynbsrv.core.models import BackendUser
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


def has_object_permission(permission_class, request, obj):
    """
    Helper function to use permission classes in @api_view functions
    """
    instance = permission_class()
    return instance.has_object_permission(request, None, obj)


def validate_object_permission(permission_class, request, obj):
    """
    Decorator function that calls has_object_permission and raises
    a PermissionDenied exception if permission is denied.
    """
    if not has_object_permission(permission_class, request, obj):
        raise PermissionDenied


class IsAuthenticatedMixin(object):

    def is_authenticated(self, request):
        return request.user and request.user.is_authenticated()


class IsManagerMixin(object):

    def is_manager(self, user, obj):
        return obj.is_manager(user)


class IsMemberMixin(object):

    def is_member(self, user, obj):
        return obj.is_member(user)


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

    def is_creator(self, user, obj):
        if type(obj.creator) == User:
            return obj.creator == user
        elif type(obj.creator) == BackendUser:
            return obj.creator == user.backend_user


class HasAccessMixin(object):

    def has_access(self, user, obj):
        return obj.has_access(user)


class IsSuperUserMixin(object):

    def is_superuser(self, user):
        return user.is_superuser


class IsAuthenticatedAndReadOnly(
        permissions.BasePermission,
        IsAuthenticatedMixin,
        IsSafeMethodMixin):
    """
    Allow all safe methods, as long as user is authenticated.
    """

    def has_permission(self, request, view):
        if self.is_authenticated(request):
            return self.is_safe_method(request)

    def has_object_permission(self, request, view, obj):
        if self.is_authenticated(request):
            return self.is_safe_method(request)


class IsSuperUser(
        permissions.BasePermission,
        IsSuperUserMixin):
    """
    Allow all, if user is superuser.
    """

    def has_permission(self, request, view):
        return self.is_superuser(request.user)

    def has_object_permission(self, request, view, obj):
        return self.is_superuser(request.user)


class IsSuperUserOrAuthenticatedAndReadOnly(
        permissions.BasePermission,
        IsAuthenticatedMixin,
        IsSuperUserMixin,
        IsSafeMethodMixin):
    """
    Allow all for superusers. Allow readonly for authenticated users.
    """

    def has_permission(self, request, view):
        if self.is_authenticated(request):
            if self.is_safe_method(request):
                return True
            if self.is_superuser(request.user):
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if self.is_authenticated(request):
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


class NotificationDetailPermission(
        permissions.BasePermission,
        HasAccessMixin,
        IsBackendUserMixin,
        IsSuperUserMixin):
    """
    Only allow access if user is superuser or has access.
    """

    def has_object_permission(self, request, view, obj):
        if self.is_superuser(request.user):
            return True
        return self.has_access(request.user, obj)


class ContainerImageDetailPermission(
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


class ContainerDetailPermission(IsSuperUserOrIsObjectOwner):
    """
    """
    pass


class ContainerSnapshotDetailPermission(
        permissions.BasePermission,
        IsBackendUserMixin,
        IsSafeMethodMixin,
        IsPublicMixin,
        IsObjectOwnerMixin,
        IsSuperUserMixin):
    """
    Todo: write doc.
    """
    def has_object_permission(self, request, view, obj):
        if self.is_public and self.is_safe_method(request):
            return True
        if self.is_superuser(request.user):
            return True
        if self.is_backend_user(request.user):
            return self.is_owner(request.user, obj.container)
        return False


class CollaborationGroupDetailPermission(
        permissions.BasePermission,
        IsSuperUserMixin,
        IsSafeMethodMixin,
        IsMemberMixin,
        IsManagerMixin,
        IsObjectCreatorMixin,
        IsPublicMixin,
        IsAuthenticatedMixin):
    """
    Permission specific for collaborationgroups.
    Only allow write actions to superusers and managers of the group,
    only allow read actions to members or authenticated users if the group is public.
    """

    def has_object_permission(self, request, view, obj):
        if self.is_safe_method(request):
            if self.is_member(request.user.backend_user, obj):
                return True
            if self.is_authenticated(request) and self.is_public(obj):
                return True
        if self.is_superuser(request.user):
            return True
        if self.is_manager(request.user.backend_user, obj):
            return True
        return False


class NotificationLogDetailPermission(
        permissions.BasePermission,
        IsSuperUserMixin):
    """
    Todo: document
    """

    def has_object_permission(self, request, view, obj):
        if self.is_superuser:
            return True
        if obj.in_use and obj.user == request.user.backend_user:
            return True
        return False


class ShareDetailPermissions(
        permissions.BasePermission,
        IsObjectOwnerMixin,
        IsSafeMethodMixin,
        IsSuperUserMixin,
        ):
    """
    Todo: document.
    """

    def has_object_permission(self, request, view, share):
        if self.is_superuser(request.user):
            return True
        if self.is_owner(request.user, share):
            return True
        if self.is_safe_method(request):
            if request.user in share.backend_group.django_group.user_set.all():
                return True
        return False
