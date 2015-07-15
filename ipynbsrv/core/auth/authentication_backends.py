from django_admin_conf_vars.global_vars import config
from django.contrib.auth.models import User
from ipynbsrv.conf import global_vars
from ipynbsrv.contract.errors import AuthenticationError,ConnectionError, GroupNotFoundError, UserNotFoundError, UserBackendError
from ipynbsrv.core import settings
from ipynbsrv.core.models import BackendUser


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
        try:
            # open connection
            global_vars.USER_BACKEND.connect({
                "username": str(username),
                "password": str(password)
            })
            # validate login credentials
            if global_vars.USER_BACKEND.validate_login({
                "username": str(username),
                "password": str(password)
            }):
                # get uidNumber for user
                uidNumber = self.get_uidNumber(username)
                # create ldap user
                self.create_internal_ldap_user(username, password, uidNumber)
                # create ldap group
                self.create_internal_ldap_group(username, uidNumber)
                # create Django user and return
                return self.create_ipynb_user(username)
            else:
                # invalid login credentials
                return None
        except AuthenticationError:
            # check if username exists on user backend
            # if not, delete zombie accounts on internal ldap & django           
            try:
                global_vars.USER_BACKEND.get_user(username)
            except UserNotFoundError:
                self.delete_user_completely(username)

        except ConnectionError:
            # server not available 
            return None

    def get_user(self, user_id):

        """
        Return the already authenticated user object.
        """

        # return backend_user for given id
        try:
            u = User.objects.get(pk=user_id)
            # check if user exists on Ldap
            l = global_vars.INTERNAL_LDAP
            #l = global_vars._get_user_backend()
            l.get_user(u.backenduser.backend_pk)
            return u
        except User.DoesNotExist:
            return None
        except:
            return None

    def delete_user_completely(self, username):
        """
        Deletes all copies of a user, including all his data (containers & shares).

        TODO: delete shares & containers
        """
        try:
            # delete user on internal ldap server
            global_vars.INTERNAL_LDAP.delete_user(username)

            # search for BackendUser objects, to not mistakenly delete regular django superusers
            u = BackendUser.objects.get(backend_pk=username)
            u.user.delete()
            u.delete()
        except:
            pass

    def get_uidNumber(self, username):

        """
        Generate a uidNumber for the user by looking at the uidNumber of the latest `ipynbsrv.core.models.BackendUser` object
        and adding it to the USER_ID_OFFSET defined in settings.py
        """

        last_django_id = 0
        if BackendUser.objects.count() > 0:
            last_django_id = BackendUser.objects.latest('id').id

        return settings.USER_ID_OFFSET + last_django_id

    def create_internal_ldap_user(self, username, password, uidNumber):
        """
        Create a copy of `username` on the internal ldap server.
        This is necessary to be able to grant access rights on the filesystem to the user.
        """

        user_creation_fields = {
            "username": str(username),
            "password": str(password),
            "uidNumber": str(uidNumber),
            "homeDirectory": str('/home/' + username),
        }

        # create user
        try:
            global_vars.INTERNAL_LDAP.get_user(username)
            # update the stored password
            global_vars.INTERNAL_LDAP.set_user_password(str(username), str(password))
        except UserNotFoundError:
            # if the user is not already in the internal ldap, create it
            # save linux user id using an offset
            try:
                global_vars.INTERNAL_LDAP.create_user(user_creation_fields)
            except Exception as ex:
                raise UserBackendError("Error while creating internal ldap user: {}".format(ex))

    def create_internal_ldap_group(self, username, uidNumber):
        """
        Create a private ldap group for `username`.
        """
        # create group
        try:
            global_vars.INTERNAL_LDAP.get_group(username)
        except GroupNotFoundError as e:
            # if the user is not already in the internal ldap, create it
            # save linux user id using an offset
            try:
                group_creation_fields = {
                    "groupname": str(username),
                    "memberUid": str(username),
                    "gidNumber": str(uidNumber)
                }
                global_vars.INTERNAL_LDAP.create_group(group_creation_fields)
            except Exception as e:
                raise UserBackendError("Error while creating internal ldap group: {}".format(e))

    def create_ipynb_user(self, username):
        """
        Create a django user (`ipynbsrv.core.models.BackendUser`) for `username`.
        This is needed to allow a more simple user management directly in django.
        """
        # 3. update django user
        try:
            backend_user = BackendUser.objects.get(backend_pk=username)
            backend_user.user.username = username
            backend_user.user.save()
        except BackendUser.DoesNotExist:
            # Create a new user. Note that we can set password
            # to anything, because it won't be checked;
            try:
                backend_user = BackendUser(backend_pk=username)
                user = User(username=username)
                user.is_staff = False
                user.is_superuser = False
                user.save()
                backend_user.user = User.objects.get(username=username)
                backend_user.save()
            except Exception as e:
                raise UserBackendError("not able to create backend_user: {}".format(e))
        u = User.objects.get(username=username)
        return u
