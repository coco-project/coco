from django_admin_conf_vars.global_vars import config
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from ipynbsrv.conf import global_vars
from ipynbsrv.contract.backends import UserBackend
from ipynbsrv.contract.errors import *
from ipynbsrv.core import settings
from ipynbsrv.core.models import BackendUser
import json
import logging


internal_ldap = global_vars.INTERNAL_LDAP
logger = logging.getLogger(__name__)
user_backend = global_vars.USER_BACKEND


# TODO: internal LDAP connect/disconnect
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
            if not BackendUser.objects.filter(user=user).exists():
                # TODO: raise PermissionDenied?
                return None  # not allowed, Django only user
            else:
                username = BackendUser.objects.filter(user=user).first().backend_pk

        try:
            internal_ldap.connect(json.loads(config.INTERNAL_LDAP_CONNECT_CREDENTIALS))
            user_backend.connect(json.loads(
                self.get_interpolated_connect_credentials(username, password)
            ))
            user_backend.auth_user(username, password)
            if user is not None:  # existing user
                internal_ldap.set_user_password(username, make_password(password))
                return user
            else:  # new user
                uid = self.generate_internal_uid()
                ldap_user = self.create_internal_ldap_user(username, password, uid)
                self.create_internal_ldap_group(username, uid)
                return self.create_django_user(username, ldap_user.get(UserBackend.FIELD_PK))
        except AuthenticationError:
            return None
        except UserNotFoundError:
            if user is not None:  # exists locally but not on backend
                # TODO: does it remove his groups?
                user.delete()
        except ConnectionError as ex:
            logger.error("Backend connection error.")
            logger.exception(ex)
            return None
        finally:  # close backend connection
            try:
                internal_ldap.disconnect()
                user_backend.disconnect()
            except:
                pass

    def create_django_user(self, username, backend_pk):
        """
        Create a django user (`ipynbsrv.core.models.BackendUser`) for `username`.
        This is needed to allow a more simple user management directly in Django.
        """
        user = User(username=username)
        user.save()
        backend_user = BackendUser(backend_pk=backend_pk, user=user)
        backend_user.save()
        return user

    def create_internal_ldap_group(self, name, gidNumber):
        """
        Create a private LDAP group for `username`.

        Attn: Exceptions are passed through (are handled in authenticate).
        """
        return internal_ldap.create_group({
            'groupname': name,
            'gidNumber': gidNumber,
            'memberUid': name
        })

    def create_internal_ldap_user(self, username, password, uidNumber):
        """
        Create a copy of `username` on the internal LDAP server.
        This is necessary to be able to grant access rights on the filesystem to the user.

        Attn: Exceptions are passed through (are handled in authenticate).
        """
        return internal_ldap.create_user({
            'username': username,
            'password': make_password(password),
            'uidNumber': uidNumber,
            'homeDirectory': '/home/' + username
        })

    def generate_internal_uid(self):
        """
        Generate an internal user ID.
        """
        last_django_id = 0
        if BackendUser.objects.count() > 0:
            last_django_id = BackendUser.objects.latest('id').id
        return settings.USER_ID_OFFSET + last_django_id

    def get_interpolated_connect_credentials(self, username, password):
        """
        Return the interpolated credentials to connect to the user backend.
        """
        return config.USER_BACKEND_CONNECT_CREDENTIALS.replace('%username%', username).replace('%password%', password)
