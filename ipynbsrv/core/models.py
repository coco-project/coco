from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.encoding import smart_unicode
from ipynbsrv.common.utils import ClassLoader
from ipynbsrv.contract.backends import ContainerBackend, SuspendableContainerBackend


class Backend(models.Model):

    """
    Model used to store references to backend implementations (as per ipynbsrv-contract package).

    Attn: The module/class needs to be installed manually. There's no magic included for this.
    """

    """
    String to identify a backend of kind 'container backend'.
    """
    CONTAINER_BACKEND = 'container_backend'

    """
    String to identify a backend of kind 'group backend'.
    """
    GROUP_BACKEND = 'group_backend'

    """
    String to identify a backend of kind 'storage backend'.
    """
    STORAGE_BACKEND = 'storage_backend'

    """
    String to identify a backend of kind 'user backend'.
    """
    USER_BACKEND = 'user_backend'

    """
    List of pluggable backends.
    """
    BACKEND_KINDS = [
        (CONTAINER_BACKEND, 'Container backend'),
        (GROUP_BACKEND, 'Group backend'),
        (STORAGE_BACKEND, 'Storage backend'),
        (USER_BACKEND, 'User backend'),
    ]

    id = models.AutoField(primary_key=True)
    kind = models.CharField(choices=BACKEND_KINDS, default=CONTAINER_BACKEND, max_length=17,
                            help_text='The kind of contract this backend fulfills.')
    module = models.CharField(max_length=255, help_text='The full absolute module path. (i.e. ipynbsrv.backends.container_backends)')
    klass = models.CharField(max_length=255, help_text='The class\' name under which it can be located within the module. (i.e. Docker or HttpRemote')
    arguments = models.CharField(blank=True, null=True, max_length=255,
                                 help_text='Optional arguments to pass to the __init__ method of the class. Format: {"arg1": "value", "arg2": "value" }')

    def get_instance(self, arguments=None):
        """
        Return an instance of the backend with either the default arguments or the one provided as an argument.

        :param arguments: If defined, use these arguments when calling the __init__ method.
        """
        cl = ClassLoader(self.module, self.klass, self.arguments)
        return cl.get_instance(arguments)

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode('%s.%s(%s)' % (self.module, self.klass, self.arguments))

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()

    class Meta:
        unique_together = ('module', 'klass', 'arguments')


class BackendGroup(models.Model):

    """
    The BackendGroup model is used to represent external backend groups.

    It is used to create Django records for internal LDAP server groups to we can work
    with them like with any other Django objects, without having to worry about the fact
    that there's a server behind.
    """
    
    backend_id = models.PositiveIntegerField(unique=True, help_text='The ID for this group used internally by the backend.')
    backend_pk = models.CharField(max_length=150, unique=True, help_text='Unique identifier for this group used by the backend.')
    django_group = models.OneToOneField(Group, related_name='backend_group', help_text='The regular Django group this backend group is associated with.')

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode(self.django_group.__str__())

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()


class BackendUser(models.Model):

    """
    The BackendUser model is used to represent external backend users.

    It is used to create Django records for internal LDAP server users to we can work
    with them like with any other Django objects, without having to worry about the fact
    that there's a server behind.
    """

    backend_id = models.PositiveIntegerField(unique=True, help_text='The ID for this user used internally by the backend.')
    backend_pk = models.CharField(max_length=150, unique=True, help_text='Unique identifier for this user used by the backend.')
    django_user = models.OneToOneField(User, related_name='backend_user', help_text='The regular Django user this backend user is associated with.')
    primary_group = models.OneToOneField('BackendGroup', related_name='primary_user', help_text='The primary backend group this user belongs to.')

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode(self.django_user.__str__())

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()


class Container(models.Model):

    """
    TODO: brief summary.
    """

    id = models.AutoField(primary_key=True)
    backend_pk = models.CharField(max_length=255, help_text='The primary key the backend uses to identify this container.')
    name = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)
    server = models.ForeignKey('Server', help_text='The server on which this container is/will be located.')
    owner = models.ForeignKey(User)
    # TODO: can this be solved more generically
    image = models.ForeignKey('Image', blank=True, null=True, help_text='The image from which this container was bootstrapped.')
    # TODO: status? better place in cache because it can easily change and we'd have to sync
    clone_of = models.ForeignKey('self', blank=True, null=True)

    def clone(self):
        """
        TODO: write doc.
        """
        raise NotImplementedError

    def create_snapshot(self, *args):
        """
        TODO: write doc.
        """
        raise NotImplementedError

    def delete_snapshot(self, *args):
        """
        TODO: write doc.
        """
        raise NotImplemented

    def get_server_backend_representation(self):
        """
        Get the representation of this container as returned by the server's container backend instance.
        """
        return self.server.get_container_backend_instance().get_container(self.backend_pk)

    def get_clones(self):
        """
        Get all containers that are clones of the one this method is called on.
        """
        return Container.objects.filter(clone_of=self)

    def get_full_name(self):
        """
        Get the full name (as it is named on the server's container backend) of this container.
        """
        # TODO: write specification
        return '%s_%s' % (self.owner.get_username(), self.name)

    def has_clones(self):
        """
        Return true if clones of this container exist, false otherwise.
        """
        return Container.objects.filter(clone_of=self).exists()

    def is_clone(self):
        """
        Return true if this container is a clone of another one.
        """
        return self.clone_of is not None

    def is_running(self):
        """
        Return true if the container is running, false otherwise.
        """
        container = self.get_server_backend_representation()
        return ContainerBackend.STATUS_RUNNING == container.get(ContainerBackend.FIELD_STATUS)

    def is_suspended(self):
        """
        Return true if the container is suspended, false otherwise.
        """
        container = self.get_server_backend_representation()
        return SuspendableContainerBackend.STATUS_SUSPENDED == container.get(ContainerBackend.FIELD_STATUS)

    def restart(self):
        """
        Restart the container.
        """
        self.server.get_container_backend_instance().restart_container(self.backend_pk)

    def resume(self):
        """
        Resume the container.
        """
        self.server.get_container_backend_instance().resume_container(self.backend_pk)

    def start(self, *args):
        """
        TODO: write doc.
        """
        raise NotImplementedError

    def stop(self):
        """
        Stop the container.
        """
        self.server.get_container_backend_instance().stop_container(self.backend_pk)

    def suspend(self):
        """
        Suspend the container.
        """
        self.server.get_container_backend_instance().suspend_container(self.backend_pk)

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode(self.get_full_name())

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()

    class Meta:
        unique_together = (
            ('backend_pk', 'server'),
            ('name', 'owner')
        )


class Image(models.Model):

    """
    TODO: brief summary.
    """

    id = models.AutoField(primary_key=True)
    backend_pk = models.CharField(unique=True, max_length=255,
                                  help_text='The primary key the backend uses to identify this image.')
    name = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User)
    snapshot_of = models.ForeignKey('Container', blank=True, null=True,
                                    related_name='snapshot_of',
                                    help_text='If not None, the container for which this image was created as a snapshot.')

    is_public = models.BooleanField(default=False)

    def get_full_name(self):
        """
        TODO: write doc.
        """
        # TODO: specification
        return '%s/%s' % (self.owner.get_username(), self.name)

    def is_snapshot(self):
        """
        Return true if this image is a container snapshot.
        """
        return self.snapshot_of is not None

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode(self.get_full_name())

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()

    class Meta:
        unique_together = ('name', 'owner')


class Server(models.Model):

    """
    TODO: brief summary.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255, help_text='The human-friendly name of this server.')
    hostname = models.CharField(unique=True, max_length=255)
    internal_ip = models.GenericIPAddressField(unique=True, protocol='IPv4',
                                               help_text='The IPv4 address of the internal ovsbr0 interface.')
    external_ip = models.GenericIPAddressField(unique=True, protocol='IPv4',
                                               help_text='The external IPv4 address of this server.')

    """
    A reference to the backend to use as a container backend on this server.
    If this field is other than 'None', the server is considered a container host.
    """
    container_backend = models.ForeignKey('Backend', blank=True, null=True, default=None,
                                          limit_choices_to={'kind': Backend.CONTAINER_BACKEND})
    container_backend_args = models.CharField(max_length=255, blank=True, null=True,
                                              help_text="""Optional arguments to pass to the backend\'s get_instance method.
                                              Available placeholders: all model fields in the form: %field_name%, e.g. %hostname%.
                                              Format: arg1=value,arg2=value""")

    def get_container_backend_instance(self):
        """
        Get an instance of the container backend this server is using.
        """
        return self.backend.get_instance(self._get_interpolated_container_backend_args())

    def _get_interpolated_container_backend_args(self):
        """
        Get the container_backend_args value with placeholders/variables replaced with their actual value.
        """
        if self.container_backend_args:
            return self.container_backend_args.replace('%name%', self.name).replace('%hostname%', self.hostname).replace('%internal_ip%', self.internal_ip).replace('%external_ip%', self.external_ip)
        return None

    def is_container_host(self):
        """
        Check if this server is configured as a container host (has a container_backend set).
        """
        return self.container_backend is not None

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode(self.name)

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()


class PortMapping(models.Model):

    """
    TODO: brief summary.
    """

    container = models.ForeignKey(Container)
    internal = models.PositiveIntegerField(null=False)
    external = models.PositiveIntegerField(unique=True)

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode("{0} ({1} -> {2})".format(self.container.__str__, self.external, self.internal))

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()


class Share(models.Model):

    """
    TODO: brief summary.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=75)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    owner = models.ForeignKey(User)
    # TODO: use OneToOneField
    group = models.ForeignKey(Group, unique=True)

    def add_member(self, user):
        """
        Add the user as a member to this group.

        :param user: The user to add.
        """
        if self.user_is_member(user):
            return False
        raise NotImplementedError

    @classmethod
    def all_user_is_member(cls, user):
        """
        Get all shares the user is a member of.

        :param cls: The class on which the method was called.
        :param user: The user object to get the shares for.
        """
        shares = []
        for share in cls.objects.all():
            if share.is_member(user):
                shares.append(share)
        return shares

    def get_members(self):
        """
        Get a list of members for this share.
        """
        return self.group.user_set.all()

    def remove_member(self, user):
        """
        Remove the member 'user' from this group.

        :param user: The member to remove.
        """
        # if not self.user_is_member(user):
        #     raise LogicError("User is not a member of the share.")
        raise NotImplementedError

    def user_is_member(self, user):
        """
        Check if the user is a member of this share.

        :param user: The user to check for membership.
        """
        return user in self.get_members()

    @classmethod
    def for_user(self, user):
        """
        TODO: document
        """
        shares = None
        try:
            shares = Share.objects.filter(owner=user.id)
        finally:
            return shares

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode(self.name)

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()


class Tag(models.Model):

    """
    TODO: brief summary.
    """

    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=75)

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode(self.label)

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()


class Notification(models.Model):

    """
    Class that acts as a message between users and groups.
    """

    """
    String to identify notifications for miscellaneous events.
    """
    MISCELLANEOUS = 'miscellaneous'

    """
    String to identify notifications for share related events.
    """
    SHARE = 'share'

    """
    String to identify notifications for container related events.
    """
    CONTAINER = 'container'

    """
    String to identify notifications for group related events.
    """
    GROUP = 'group'

    """
    String to identify notifications for image related events.
    """
    IMAGE = 'image'

    """
    List of choosable event event types.
    """
    EVENT_TYPES = [
        (MISCELLANEOUS, 'Miscellaneous'),
        (SHARE, 'Share'),
        (CONTAINER, 'Container'),
        (GROUP, 'Group'),
        (IMAGE, 'Image')
    ]

    sender = models.ForeignKey(User, help_text='The user who send the notification.')
    message = models.CharField(max_length=255, help_text='The message body.')
    date = models.DateTimeField()
    event_type = models.CharField(choices=EVENT_TYPES, default=MISCELLANEOUS, max_length=20)

    def send(self):
        to_send = NotificationReceivers.objects.filter(notification=self.id)

        # TODO: avoid double notifications
        for n in to_send:
            for user in n.receiving_group.user_set.all():
                notification_log = NotificationLog(notification=self, user=user)
                notification_log.save()

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode("{0}: {1}".format(self.date, self.message))

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()


class NotificationReceivers(models.Model):

    """
    Helper class to allow multiple receivers per Notification.
    """

    notification = models.ForeignKey(Notification)
    receiving_group = models.ForeignKey(Group, help_text='The regular Django group that will receive this Notification.')


class NotificationLog(models.Model):

    """
    Keep track of all the notifications per user and if they have been read yet.
    """

    notification = models.ForeignKey(Notification, help_text='The notification itself.')
    user = models.ForeignKey(User, related_name='user', help_text='The BackendUser assigned to this NotificationLog entry.')
    read = models.BooleanField(default=False)

    @classmethod
    def for_user(self, user):
        """
        TODO: document
        """
        notifications = None
        try:
            notifications = NotificationLog.objects.filter(user=user.id).order_by("-notification__date")
        finally:
            return notifications


# make sure our signal receivers are loaded
from ipynbsrv.core.signals import groups, users
