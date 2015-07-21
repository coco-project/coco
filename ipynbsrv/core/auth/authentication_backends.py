from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, User
from ipynbsrv.conf.helpers import *
from ipynbsrv.contract.backends import GroupBackend, UserBackend
from ipynbsrv.contract.errors import *
from ipynbsrv.core import settings
from ipynbsrv.core.models import BackendGroup, BackendUser
import logging


logger = logging.getLogger(__name__)


class BackendProxyAuthentication(object):

    """
    Class used to authenticate with the user backends.

    more info: https://docs.djangoproject.com/en/1.8/topics/auth/default/#django.contrib.auth.authenticate
    """

    def authenticate(self, username=None, password=None):
        """
        :param username
        :param password

        :return User object     if login credentials are valid
                None            if login credentials are invalid

        :raise  PermissionDenied    to immediately cancel authentication,
                                    no other AuthenticationBackend will be checked after this
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
                internal_ldap.set_user_credential(username, make_password(password))  # FIXME: handle in signals
                return user
            else:  # new user
                uid = BackendProxyAuthentication.generate_internal_uid()
                group = self.create_user_groups(username, uid)
                user = self.create_users(username, uid, group.backend_group)
                # add user to group
                group.user_set.add(user)
                return user
        except AuthenticationError:
            return None
        except UserNotFoundError:
            if user is not None:  # exists locally but not on backend
                user.delete()
        except ConnectionError as ex:
            logger.error("Backend connection error.")
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
        Creates the Django groups for the logging-in user.

        :param name: The name of the group to create.
        :param gid: The group's ID (on the backend).
        """
        group = Group(name=name)
        group.save()
        backend_group = BackendGroup(backend_id=gid, backend_pk=name, django_group=group)
        backend_group.save()
        return group

    def create_users(self, username, uid, primary_group):
        """
        Creates the Django users for the logging-in user.

        :param username: The user's username.
        :param primary_group: The user's primary group.
        """
        user = User(username=username)
        user.save()
        backend_user = BackendUser(backend_id=uid, backend_pk=username, django_user=user, primary_group=primary_group)
        backend_user.save()
        return user

    @classmethod
    def generate_internal_uid(self):
        """
        Generate an internal user ID.

        TODO: make static method on BackendGroup/User?
        """
        last_django_id = 0
        if BackendUser.objects.count() > 0:
            last_django_id = BackendUser.objects.latest('id').id
        return settings.USER_ID_OFFSET + last_django_id

    @classmethod
    def generate_internal_guid(self):
        """
        Generate an internal group ID.
        Used for user-created groups. The primary group of each user should use the user's uid as guid.

        TODO: make static method on BackendGroup/User?
        """
        last_django_id = 0
        if Group.objects.count() > 0:
            last_django_id = Group.objects.latest('id').id
        return settings.GROUP_ID_OFFSET + last_django_id

    def get_user(self, user_id):
        """
        :inherit
        """
        try:
            return User.objects.get(pk=user_id)
        except Exception:
            return None