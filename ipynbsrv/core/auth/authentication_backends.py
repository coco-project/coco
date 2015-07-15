from django_admin_conf_vars.global_vars import config
from django.contrib.auth.models import User
from ipynbsrv.conf import global_vars
from ipynbsrv.contract.errors import GroupNotFoundError, UserNotFoundError
from ipynbsrv.core import settings
from ipynbsrv.core.models import BackendUser


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
                    if BackendUser.objects.count() > 0:
                        last_django_id = BackendUser.objects.latest('id').id

                    uidNumber = settings.USER_ID_OFFSET + last_django_id

                    user_creation_fields = {
                        "username": str(username),
                        "password": str(password),
                        "uidNumber": str(uidNumber),
                        "homeDirectory": str('/home/'+ username),
                    }

                    # create user
                    try:
                        print("-->try to get user from internal ldap")
                        internal_ldap.get_user(username)
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

                    # create group
                    try:
                        print("-->try to get group from internal ldap")
                        internal_ldap.get_group(username)
                    except GroupNotFoundError as e:
                        # if the user is not already in the internal ldap, create it
                        # save linux user id using an offset
                        print("group not found on internal ldap")
                        try:
                            group_creation_fields = {
                                "groupname": str(username),
                                "memberUid": str(username),
                                "gidNumber": str(uidNumber)
                            }
                            internal_ldap.create_group(group_creation_fields)
                        except Exception as e:
                            print("error creating internal ldap group")
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
                    backend_user = BackendUser.objects.get(backend_pk=username)
                    print("backend_user exists {0}".format(backend_user.backend_pk))
                    backend_user.user.username = username
                    backend_user.user.save()
                except backend_user.DoesNotExist:
                    # Create a new user. Note that we can set password
                    # to anything, because it won't be checked;
                    try:
                        print("backend_user does not exist {0}".format(username))
                        user_data = internal_ldap.get_user(username)
                        backend_user = BackendUser(backend_user=username)
                        print("backend_user obj: {0}".format(backend_user))
                        user = User(username=username)
                        user.is_staff = False
                        user.is_superuser = False
                        print("user obj: {0}".format(user))
                        user.save()
                        backend_user.user = User.objects.get(username=username)
                        backend_user.save()
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
        :inherit.
        """
        # return ipynbuser for given id
        try:
            print("------------------------------")
            print("> get_user() {}".format(user_id))
            u = User.objects.get(pk=user_id)
            # check if user exists on Ldap
            l = global_vars.INTERNAL_LDAP
            #l = global_vars._get_user_backend()
            l.get_user(u.backenduser.identifier)
            print("user found {}".format(u))
            print("------------------------------")
            return u
        except User.DoesNotExist:
            return None
        except:
            return None
