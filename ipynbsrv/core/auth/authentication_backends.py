from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from ipynbsrv.contract.errors import AuthenticationError, ConnectionError, \
    UserNotFoundError
from ipynbsrv.core.helpers import get_user_backend_connected
from ipynbsrv.core.models import BackendGroup, BackendUser, \
    CollaborationGroup
import logging


logger = logging.getLogger(__name__)


class BackendProxyAuthentication(object):

    """
    Class used to authenticate with the user backends.

    more info: https://docs.djangoproject.com/en/1.8/topics/auth/default/#django.contrib.auth.authenticate
    """

    def authenticate(self, username=None, password=None):
        """
        :inherit.
        """
        # check if the user already exists in our system
        # if so, use the defined backend_pk for validating the credentials on the backend
        # if its a Django only user, disallow the login
        user = None
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if hasattr(user, 'backend_user'):
                username = user.backend_user.backend_pk
            else:
                return None  # not allowed, Django only user

        try:
            user_backend = get_user_backend_connected()
            user_backend.auth_user(username, password)
            if user is not None:  # existing user
                if not user.check_password(password):
                    user.set_password(password)
                    user.save()
            else:  # new user
                uid = BackendUser.generate_internal_uid()
                group = self.create_user_groups(username, uid)
                user = self.create_users(username, password, uid, group.backend_group)
                group.add_member(user.backend_user)

            if user.is_active:
                return user
            else:
                return None
        except AuthenticationError:
            raise PermissionDenied
        except UserNotFoundError:
            if user is not None:  # exists locally but not on backend
                user.delete()
        except ConnectionError as ex:
            logger.exception(ex)
            return None
        finally:
            try:
                internal_ldap.disconnect()
                user_backend.disconnect()
            except:
                pass

    def create_user_groups(self, name, gid):
        """
        Create the groups for the logging-in user.

        :param name: The name of the group to create.
        :param gid: The group's ID (on the backend).
        """
        collaboration_group = CollaborationGroup(
            name=name,
            is_single_user_group=True
        )
        collaboration_group.save()
        backend_group = BackendGroup(
            django_group=collaboration_group,
            backend_id=gid,
            backend_pk=name
        )
        backend_group.save()
        return collaboration_group

    def create_users(self, username, password, uid, primary_group):
        """
        Create the Django users for the logging-in user.

        :param username: The user's username.
        :param primary_group: The user's primary group.
        """
        user = User(username=username, password=password)
        user.save()
        backend_user = BackendUser(
            django_user=user,
            backend_id=uid,
            backend_pk=username,
            primary_group=primary_group
        )
        backend_user.save()
        return user

    def get_user(self, user_id):
        """
        :inherit.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
