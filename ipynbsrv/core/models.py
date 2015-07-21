from datetime import datetime
from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.encoding import smart_unicode
from ipynbsrv.common.utils import ClassLoader
from ipynbsrv.contract.backends import ContainerBackend, SuspendableContainerBackend
from ipynbsrv.core import settings
import re


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
    kind = models.CharField(
        choices=BACKEND_KINDS,
        default=CONTAINER_BACKEND,
        max_length=17,
        help_text='The kind of contract this backend fulfills.'
    )
    module = models.CharField(
        max_length=255,
        help_text='The full absolute module path (i.e. ipynbsrv.backends.container_backends).'
    )
    klass = models.CharField(
        max_length=255,
        help_text='The class\' name under which it can be located within the module (i.e. Docker or HttpRemote).'
    )
    arguments = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text="""Optional arguments to pass to the __init__ method of the class.
            Format: {"arg1": "value", "arg2": "value" }"""
    )

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

    It is used to create Django records for internal LDAP server groups so we can work
    with them like with any other Django objects, without having to worry about the fact
    that there's a server behind.
    """

    id = models.AutoField(primary_key=True)
    backend_id = models.PositiveIntegerField(
        unique=True,
        help_text='The ID for this group used internally by the backend.'
    )
    backend_pk = models.CharField(
        unique=True,
        max_length=255,
        help_text='Unique identifier for this group used by the backend.'
    )
    django_group = models.OneToOneField(
        Group,
        related_name='backend_group',
        help_text='The regular Django group this backend group is associated with.'
    )

    @classmethod
    def generate_internal_guid(self):
        """
        Generate an unique internal group ID.

        Used for user-created groups. The primary group of each user should use the user's uid as guid.
        """
        last_django_id = 0
        if Group.objects.count() > 0:
            last_django_id = Group.objects.latest('id').id
        return settings.GROUP_ID_OFFSET + last_django_id

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

    It is used to create Django records for internal LDAP server users so we can work
    with them like with any other Django objects, without having to worry about the fact
    that there's a server behind.
    """

    id = models.AutoField(primary_key=True)
    backend_id = models.PositiveIntegerField(
        unique=True,
        help_text='The ID for this user used internally by the backend.')
    backend_pk = models.CharField(
        unique=True,
        max_length=255,
        help_text='Unique identifier for this user used by the backend.'
    )
    django_user = models.OneToOneField(
        User,
        related_name='backend_user',
        help_text='The regular Django user this backend user is associated with.'
    )
    primary_group = models.OneToOneField(
        'BackendGroup',
        related_name='primary_user',
        help_text='The primary backend group this user belongs to.'
    )

    @classmethod
    def generate_internal_uid(self):
        """
        Generate an unique internal user ID.
        """
        last_django_id = 0
        if BackendUser.objects.count() > 0:
            last_django_id = BackendUser.objects.latest('id').id
        return settings.USER_ID_OFFSET + last_django_id

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
    The Container model is used to represent external container_backend instances.
    """

    id = models.AutoField(primary_key=True)
    backend_pk = models.CharField(
        max_length=255,
        help_text='The primary key the backend uses to identify this container.'
    )
    name = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)
    server = models.ForeignKey(
        'Server',
        help_text='The server on which this container is/will be located.'
    )
    owner = models.ForeignKey('BackendUser')
    # ImageBasedContainerBackend
    image = models.ForeignKey(
        'ContainerImage',
        blank=True,
        null=True,
        help_text='The image from which this container was bootstrapped.'
    )
    # CloneableContainerBackend
    clone_of = models.ForeignKey('self', blank=True, null=True)

    def clone(self):
        """
        TODO: write doc.
        """
        self.server.get_container_backend().clone_container(self.backend_pk, {})

    def create_snapshot(self, name, description):
        """
        Create a snapshot of the current container state.

        :param name: The snapshot's name.
        :param description: The snapshot's description.
        """
        snapshot = ContainerSnapshot(
            backend_pk=0,
            name=name,
            description=description,
            container=self
        )
        snapshot.save()
        from ipynbsrv.core.signals.signals import container_snapshot_created
        container_snapshot_created.send(sender=self, snapshot=snapshot)
        return snapshot

    def get_server_backend_representation(self):
        """
        Get the representation of this container as returned by the server's container backend instance.
        """
        return self.server.get_container_backend().get_container(self.backend_pk)

    def get_clones(self):
        """
        Get all containers that are clones of the one this method is called on.
        """
        return Container.objects.filter(clone_of=self)

    def get_backend_name(self):
        """
        Return the name of this container how it is named on the backend.
        """
        return "%s%i_%s" % (settings.CONTAINER_NAME_PREFIX, self.owner.backend_id, self.name)

    def get_friendly_name(self):
        """
        Return the humen-friendly name of this container.
        """
        return self.owner.django_user.get_username() + '_' + self.name

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

        TODO: store in cache?
        """
        ct = self.get_server_backend_representation()
        return ct.get(ContainerBackend.CONTAINER_KEY_STATUS) \
            == ContainerBackend.CONTAINER_STATUS_RUNNING

    def is_suspended(self):
        """
        Return true if the container is suspended, false otherwise.

        TODO: store in cache?
        """
        ct = self.get_server_backend_representation()
        return ct.get(ContainerBackend.CONTAINER_KEY_STATUS) \
            == SuspendableContainerBackend.CONTAINER_STATUS_SUSPENDED

    def restart(self):
        """
        Restart the container.
        """
        from ipynbsrv.core.signals.signals import container_restarted
        container_restarted.send(sender=self, container=self)

    def resume(self):
        """
        Resume the container.
        """
        from ipynbsrv.core.signals.signals import container_resumed
        container_resumed.send(sender=self, container=self)

    def start(self, *args):
        """
        Start the container.
        """
        from ipynbsrv.core.signals.signals import container_started
        container_started.send(sender=self, container=self)

    def stop(self):
        """
        Stop the container.
        """
        from ipynbsrv.core.signals.signals import container_stopped
        container_stopped.send(sender=self, container=self)

    def suspend(self):
        """
        Suspend the container.
        """
        if self.is_running() and not self.is_suspended():
            from ipynbsrv.core.signals.signals import container_suspended
            container_suspended.send(sender=self, container=self)

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode(self.get_friendly_name())

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


class ContainerImage(models.Model):

    """
    Model to reference container_backend images/templates which can be used to bootstrap containers.
    """

    id = models.AutoField(primary_key=True)
    backend_pk = models.CharField(
        unique=True,
        max_length=255,
        help_text='The primary key the backend uses to identify this image.'
    )
    name = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)
    # TODO: document placeholders
    command = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text='The command to execute inside the container upon start.'
    )
    owner = models.ForeignKey(User)
    is_public = models.BooleanField(default=False)

    def get_backend_name(self):
        """
        Return the name of this image how it is named on the backend.
        """
        return "%s%i/%s" % (settings.CONTAINER_IMAGE_NAME_PREFIX, self.owner.backend_id, self.name)

    def get_friendly_name(self):
        """
        Return the humen-friendly name of this image.
        """
        if hasattr(self.owner, 'backend_user'):
            return self.owner.get_username() + '/' + self.name
        else:
            return self.name

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode(self.get_friendly_name())

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()

    class Meta:
        unique_together = ('name', 'owner')


class ContainerSnapshot(models.Model):

    """
    Model to reference container_backend snapshots of container instances.
    """

    id = models.AutoField(primary_key=True)
    backend_pk = models.CharField(
        unique=True,
        max_length=255,
        help_text='The primary key the backend uses to identify this snapshot.'
    )
    name = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)
    container = models.ForeignKey('Container')

    def get_backend_name(self):
        """
        Return the name of this snapshot how it is named on the backend.
        """
        container_name = self.container.get_backend_name()
        repository = re.sub(
            r'^' + settings.CONTAINER_NAME_PREFIX + r'(\d+)_(.+)$',
            settings.CONTAINER_NAME_PREFIX + r'\g<1>/\g<2>',
            container_name
        )
        tag = settings.CONTAINER_SNAPSHOT_PREFIX + self.name
        return repository + ':' + tag

    def get_friendly_name(self):
        """
        Return the humen-friendly name of this container snapshot.
        """
        return self.container.get_friendly_name() + ':' + self.name

    def restore(self):
        """
        TODO: write doc.
        """
        pass

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode(self.get_friendly_name())

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()

    class Meta:
        unique_together = ('name', 'container')


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
    date = models.DateTimeField(default=datetime.now())
    event_type = models.CharField(
        choices=EVENT_TYPES,
        default=MISCELLANEOUS,
        max_length=20
    )

    def send(self):
        """
        TODO: write doc.
        """
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


class NotificationLog(models.Model):

    """
    Keep track of all the notifications per user and if they have been read yet.
    """

    notification = models.ForeignKey(
        Notification,
        help_text='The notification itself.'
    )
    user = models.ForeignKey(
        User,
        related_name='user',
        help_text='The BackendUser assigned to this NotificationLog entry.'
    )
    read = models.BooleanField(default=False)

    @classmethod
    def for_user(self, user):
        """
        TODO: document.
        """
        notifications = None
        try:
            notifications = NotificationLog.objects.filter(user=user.id).order_by("-notification__date")
        finally:
            return notifications


class NotificationReceivers(models.Model):

    """
    Helper class to allow multiple receivers per Notification.
    """

    notification = models.ForeignKey(Notification)
    receiving_group = models.ForeignKey(
        Group,
        help_text='The regular Django group that will receive this Notification.'
    )


class Server(models.Model):

    """
    Django model to represent an ipynbsrv setup node.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(
        unique=True,
        max_length=255,
        help_text='The human-friendly name of this server.'
    )
    hostname = models.CharField(unique=True, max_length=255)
    internal_ip = models.GenericIPAddressField(
        unique=True,
        protocol='IPv4',
        help_text='The IPv4 address of the internal ovsbr0 interface.'
    )
    external_ip = models.GenericIPAddressField(
        unique=True,
        protocol='IPv4',
        help_text='The external IPv4 address of this server.'
    )

    """
    A reference to the backend to use as a container backend on this server.
    If this field is other than 'None', the server is considered a container host.
    """
    container_backend = models.ForeignKey(
        'Backend',
        blank=True,
        null=True,
        default=None,
        limit_choices_to={'kind': Backend.CONTAINER_BACKEND}
    )
    container_backend_args = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text="""Optional arguments to pass to the backend\'s get_instance method.
            Available placeholders: all model fields in the form: %field_name%, e.g. %hostname%.
            Format: {'arg1': \"value\", 'arg2': \"value\"}"""
    )

    def get_container_backend(self):
        """
        Get an instance of the container backend this server is using.
        """
        return self.container_backend.get_instance(self._get_interpolated_container_backend_args())

    def _get_interpolated_container_backend_args(self):
        """
        Get the container_backend_args value with placeholders/variables replaced with their actual value.
        """
        if self.container_backend_args:
            return self.container_backend_args \
                .replace('%name%', self.name) \
                .replace('%hostname%', self.hostname) \
                .replace('%internal_ip%', self.internal_ip) \
                .replace('%external_ip%', self.external_ip)
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
    group = models.OneToOneField(Group, related_name='share')

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


# make sure our signal receivers are loaded
from ipynbsrv.core.signals import *
