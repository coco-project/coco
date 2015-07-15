from django_admin_conf_vars.global_vars import config
from django.contrib.auth.models import User
from ipynbsrv.conf import global_vars
from ipynbsrv.contract.errors import UserNotFoundError
from ipynbsrv.core.models import IpynbUser


# TODO: make dynamic
class BackendProxyAuthentication(object):

    """
    TODO: write doc.
    """

    def authenticate(self, username=None, password=None):
        """
        TODO: write doc.
        """
        # 1. check login credentials with user backend
        user_be = global_vars.USER_BACKEND
        internal_ldap = global_vars.INTERNAL_LDAP

        try:
            print("connect {0}@{1} mit Passwort {2}".format(username, user_be.server, password))

            # open connection
            user_be.connect({
                "username": username,
                "password": password
            })

            if user_be.validate_login({
                "username": username,
                "password": password
            }):
                # 2. create user in internal ldap
                try:
                    user_data = user_be.get_user(username)
                    config.set('LAST_INTERNAL_LDAP_USER_ID', config.LAST_INTERNAL_LDAP_USER_ID+1)
                    user_creation_fields = {
                        "username": username,
                        "password": password,
                        "uidNumber": str(config.LAST_INTERNAL_LDAP_USER_ID)
                    }
                    """
                    for field in credentials:
                        if field in required_user_creation_fields:
                            user_creation_fields[field] = required_user_creation_fields[field]
                    """
                    try:
                        internal_user_data = internal_ldap.get_user(username)
                        # update the stored password
                        # TODO: no plaintext! use md5 or similar
                        internal_ldap.set_user_password(username, password)
                        print("user already existing in internal ldap")
                    except UserNotFoundError as e:
                        # if the user is not already in the internal ldap, create it
                        # save linux user id using an offset
                        try:
                            internal_ldap.create_user(user_creation_fields)
                        except:
                            print("error creating internal ldap user")
                    except:
                        print("some other error")

                except Exception as e:
                    print("failed to create user on internal ldap")
                    print(e)
                    return None

                # 3. update django user
                try:
                    ipynbuser = IpynbUser.objects.get(identifier=username)
                    print("ipynbuser exists {0}".format(ipynbuser.identifier))
                    ipynbuser.user.username = username
                    ipynbuser.user.save()
                except IpynbUser.DoesNotExist:
                    # Create a new user. Note that we can set password
                    # to anything, because it won't be checked;
                    try:
                        print("ipynbuser does not exist {0}".format(username))
                        user_data = user_be.get_user(username)
                        print("ldap lookup: {0}".format(user_data))
                        ipynbuser = IpynbUser(identifier=username, home_directory=user_data['homeDirectory'][0])
                        print("ipynbuser obj: {0}".format(ipynbuser))
                        user = User(username=username)
                        user.is_staff = False
                        user.is_superuser = False
                        print("user obj: {0}".format(user))
                        user.save()
                        ipynbuser.user = User.objects.get(username=username)
                        ipynbuser.save()
                    except Exception as e:
                        print("not able to create ipynbuser")
                        print(e)
                        return None
                u = User.objects.get(username=username)
                print("return {0}".format(str(u)))
                return u
                # 4. return user object
            else:
                return None
        except:
            print("connect failed")
            return None


        # TODO: always close connection
        print "LDAP Authentication successful!"

    def get_user(self, user_id):
        """
        :inherit.
        """
        # return ipynbuser for given id
        try:
            print("get user {}".format(user_id))
            u = User.objects.get(pk=user_id)
            # check if user exists on Ldap
            l = global_vars._get_user_backend()
            l.get_user(u.ipynbuser.identifier)
            print("user found {}".format(u))
            return u
        except User.DoesNotExist:
            return None
