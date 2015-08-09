from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from ipynbsrv.core.auth.authentication_backends import BackendProxyAuthentication
from ipynbsrv.core.helpers import get_user_backend_connected
from ipynbsrv.core.models import *
from ipynbsrv.contract.backends import UserBackend


def import_users():
    """
    Imports all the users found on the user backend into django.
    """
    backend = get_user_backend_connected()
    users = backend.get_users()
    helper = BackendProxyAuthentication()
    new_users = []
    for user in users:
        username = str(user.get(UserBackend.FIELD_PK))
        password = ''
        obj = User.objects.filter(username=username)
        if not obj:
            # if user is not existing yet, create him
            uid = BackendUser.generate_internal_uid()
            group = helper.create_user_groups(username, uid)
            user = helper.create_users(username, password, uid, group.backend_group)
            group.add_user(user.backend_user)
            new_users.append(username)
    return new_users


class Command(BaseCommand):

    """
    Custom manage.py command to import users from the user backend.

    https://docs.djangoproject.com/en/1.8/howto/custom-management-commands/
    """

    help = 'Import all users from the UserBackend defined in the config vars.'

    # def add_arguments(self, parser):
    # Todo: make command more powerful, to import single users by username
    #     parser.add_argument('username', nargs='+', type=str)

    def handle(self, *args, **options):
        new_users = import_users()
        self.stdout.write("Successfully imported {} users:".format(len(new_users)))
        for user in new_users:
            self.stdout.write(user)
