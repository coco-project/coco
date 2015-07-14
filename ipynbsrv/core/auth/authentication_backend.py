from ipynbsrv.conf import global_vars
from ipynbsrv.core.models import IpynbUser
from ipynbsrv.core import settings
from ipynbsrv.contract.errors import UserNotFoundError
from django.contrib.auth.models import User
from django_admin_conf_vars.global_vars import config


# TODO: make dynamic
class IpynbsrvAuthentication(object):
    """

    """
    def authenticate(self, username=None, password=None):

        # 1. check login credentials with user backend
        user_be = global_vars._get_user_backend()
        internal_ldap = global_vars._get_internal_ldap()

        try:
            print("------------------------------")
            print("authenticate")
            print("connect {0}@{1} mit Passwort".format(username, user_be.server))

            # open connection
            user_be.connect({
                "username": str(username),
                "password": str(password)
            })

            if user_be.validate_login({
                "username": str(username),
                "password": str(password)
            }):
                # 2. create user in internal ldap
                try:
                    user_data = user_be.get_user(username)
                    last_django_id = 0
                    if IpynbUser.objects.count() > 0:
                        last_django_id = IpynbUser.objects.latest('id').id

                    user_creation_fields = {
                        "username": str(username),
                        "password": str(password),
                        "uidNumber": str(settings.UNIX_USER_OFFSET + last_django_id)
                    }

                    print("user_creation_fields: {}".format(user_creation_fields))

                    try:
                        print("-->try to get user from internal ldap")
                        internal_user_data = internal_ldap.get_user(username)
                        # update the stored password
                        # TODO: no plaintext! use md5 or similar
                        internal_ldap.set_user_password(str(username), str(password))
                        print("user already existing in internal ldap")
                    except UserNotFoundError as e:
                        # if the user is not already in the internal ldap, create it
                        # save linux user id using an offset
                        print("user not found on internal ldap")
                        try:
                            internal_ldap.create_user(user_creation_fields)
                        except Exception as e:
                            print("error creating internal ldap user")
                            print(e)
                            raise(e)
                    except Exception as e:
                        print("some other error")
                        print(e)
                        raise(e)

                except Exception as e:
                    print("failed to create user on internal ldap")
                    raise(e)
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
                print("------------------------------")
                return u
                # 4. return user object
            else:
                return None
        except Exception as e:
            print("connect failed")
            return None


        # TODO: always close connection
        print "LDAP Authentication successful!"

    def get_user(self, user_id):
        """

        """
        # return ipynbuser for given id
        try:
            print("------------------------------")
            print("> get_user() {}".format(user_id))
            u = User.objects.get(pk=user_id)
            # check if user exists on Ldap
            l = global_vars._get_internal_ldap()
            #l = global_vars._get_user_backend()
            l.get_user(u.ipynbuser.identifier)
            print("user found {}".format(u))
            print("------------------------------")
            return u
        except User.DoesNotExist:
            return None
        except:
            return None
