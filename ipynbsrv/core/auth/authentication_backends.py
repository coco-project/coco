from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, User
from ipynbsrv.contract.errors import AuthenticationError, ConnectionError, \
    UserNotFoundError
from ipynbsrv.core.helpers import get_internal_ldap_connected, get_user_backend_connected
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
            if not hasattr(user, 'backend_user'):
                return None  # not allowed, Django only user
            else:
                username = user.backend_user.backend_pk

        internal_ldap = get_internal_ldap_connected()
        user_backend = get_user_backend_connected()
        try:
            user_backend.auth_user(username, password)
            if user is not None:  # existing user
                internal_ldap.set_user_password(username, make_password(password))  # FIXME: handle in signals
                auth = user
            else:  # new user
                uid = BackendUser.generate_internal_uid()
                group = self.create_user_groups(username, uid)
                user = self.create_users(username, uid, group.backend_group)
                # add user to group
                group.user_set.add(user)
                auth = user

            if auth.is_active:
                return auth
            else:
                return None
        except AuthenticationError:
            return None
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
        Create the Django groups for the logging-in user.

        :param name: The name of the group to create.
        :param gid: The group's ID (on the backend).
        """
        group = Group(name=name)
        group.save()
        backend_group = BackendGroup(
            django_group=group,
            backend_id=gid,
            backend_pk=name
        )
        backend_group.save()
        collaboration_group = CollaborationGroup(
            django_group=group
        )
        collaboration_group.save()
        return group

    def create_users(self, username, uid, primary_group):
        """
        Create the Django users for the logging-in user.

        :param username: The user's username.
        :param primary_group: The user's primary group.
        """
        user = User(username=username)
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
        except Exception:
            return None
