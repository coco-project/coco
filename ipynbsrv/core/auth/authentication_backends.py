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
                internal_ldap.set_user_credential(username, make_password(password))
                return user
            else:  # new user
                uid = self.generate_internal_uid()
                # create internal LDAP records
                # TODO: actions on external resources/backends should be placed
                # in signals? The following two statements as well...
                ldap_group = internal_ldap.create_group({
                    'groupname': username,
                    'gidNumber': uid
                })
                print ldap_group
                ldap_user = internal_ldap.create_user({
                    'username': username,
                    'password': make_password(password),
                    'uidNumber': uid,
                    'gidNumber': uid,
                    'homeDirectory': '/home/' + username
                })
                # add user to group
                internal_ldap.add_group_member(ldap_group.get(GroupBackend.FIELD_PK), ldap_user.get(UserBackend.FIELD_PK))
                # create Django records
                group = self.create_django_group(username, ldap_group.get(GroupBackend.FIELD_PK), uid)
                user = self.create_django_user(username, ldap_user.get(UserBackend.FIELD_PK), uid, group.backend_group)
                # add user to group
                user.backend_user.save()
                user.save()
                group.user_set.add(user)
                group.save()

                print("{} added to {}".format(user, group))

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

    def create_django_group(self, groupname, backend_pk, backend_id):
        """
        Create a django group (`ipynbsrv.core.models.BackendGroup`) for `username`.
        This is needed to allow a more simple group management directly in Django.
        """
        group = Group(name=groupname)
        group.save()
        backend_group = BackendGroup(backend_pk=backend_pk, backend_id=backend_id, django_group=group)
        backend_group.save()
        return group

    def create_django_user(self, username, backend_pk, backend_id, group):
        """
        Create a django user (`ipynbsrv.core.models.BackendUser`) for `username`.
        This is needed to allow a more simple user management directly in Django.
        """
        user = User(username=username)
        user.save()
        backend_user = BackendUser(backend_pk=backend_pk, django_user=user, backend_id=backend_id, primary_group=group)
        backend_user.save()
        return user

    def generate_internal_uid(self):
        """
        Generate an internal user ID.
        """
        last_django_id = 0
        if BackendUser.objects.count() > 0:
            last_django_id = BackendUser.objects.latest('id').id
        return settings.USER_ID_OFFSET + last_django_id

    def get_user(self, user_id):
        """
        :inherit
        """
        try:
            return User.objects.get(pk=user_id)
        except Exception:
            return None
