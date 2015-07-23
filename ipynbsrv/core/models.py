from datetime import datetime
from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.encoding import smart_unicode
from ipynbsrv.common.utils import ClassLoader
from ipynbsrv.contract.backends import ContainerBackend, SuspendableContainerBackend
from ipynbsrv.core import settings
from random import randint


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

    @staticmethod
    def generate_internal_guid():
        """
        Generate an unique internal group ID.

        Used for user-created groups. The primary group of each user should use the user's uid as guid.
        """
        last_django_id = 0
        if Group.objects.count() > 0:
            last_django_id = Group.objects.latest('id').id
        return settings.GROUP_ID_OFFSET + last_django_id

    id = models.AutoField(primary_key=True)
    backend_id = models.PositiveIntegerField(
        unique=True,
        help_text='The ID for this group used internally by the backend.'
    )
    backend_pk = models.CharField(
        unique=True,
        default=randint(0, 1000),
        max_length=255,
        help_text='Unique identifier for this group used by the backend.'
    )
    django_group = models.OneToOneField(
        Group,
        related_name='backend_group',
        help_text='The regular Django group this backend group is associated with.'
    )
    creator = models.ForeignKey(
        User,
        blank=True,
        null=True,
        help_text='The user that created the group.'
    )
    admins = models.ManyToManyField(
        User,
        related_name='managed_groups',
        help_text='The users that are allowed to manage the group.'
    )

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

    @staticmethod
    def generate_internal_uid():
        """
        Generate an unique internal user ID.
        """
        last_django_id = 0
        if BackendUser.objects.count() > 0:
            last_django_id = BackendUser.objects.latest('id').id
        return settings.USER_ID_OFFSET + last_django_id

    id = models.AutoField(primary_key=True)
    backend_id = models.PositiveIntegerField(
        unique=True,
        help_text='The ID for this user used internally by the backend.'
    )
    backend_pk = models.CharField(
        unique=True,
        default=randint(0, 1000),
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
    public = models.BooleanField(
        default=False,
        help_text='Indicate if the group should be publicly visible and free to join for everyone.'
    )

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
        default=randint(0, 1000),
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
    image = models.ForeignKey(
        'ContainerImage',
        blank=True,
        null=True,
        help_text='The image from which this container was bootstrapped.'
    )
    clone_of = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        help_text='The container on which this one is based/was cloned from.'
    )

    def clone(self, name, description=None):
        """
        TODO: write doc.
        """
        if description is None:
            description = self.description

        clone = Container(
            name=name,
            description=description,
            server=self.server,
            owner=self.owner,
            clone_of=self
        )
        clone.save()

        from ipynbsrv.core.signals.signals import container_cloned
        container_cloned.send(sender=self, container=self, clone=clone)

        return clone

    def create_snapshot(self, name, description=None):
        """
        Create a snapshot of the current container state.

        :param name: The snapshot's name.
        :param description: The snapshot's description.
        """
        snapshot = ContainerSnapshot(
            name=name,
            description=description,
            container=self
        )
        snapshot.save()
        return snapshot

    def get_clones(self):
        """
        Get all containers that are clones of the one this method is called on.
        """
        return Container.objects.filter(clone_of=self)

    def get_backend_name(self):
        """
        Return the container name the way it is passed to the backend upon creation.
        """
        return 'u%i-%s' % (self.owner.backend_id, self.name)

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

    def is_image_based(self):
        """
        Return either this container was created based on an image or not.
        """
        return self.image is not None

    def is_running(self):
        """
        Return true if the container is running, false otherwise.

        TODO: store in cache?
        """
        return self.server.get_container_backend().container_is_running(self.backend_pk)

    def is_suspended(self):
        """
        Return true if the container is suspended, false otherwise.

        TODO: store in cache?
        """
        return self.server.get_container_backend().container_is_suspended(self.backend_pk)

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
        default=randint(0, 1000),
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
    is_internal = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

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
        default=randint(0, 1000),
        max_length=255,
        help_text='The primary key the backend uses to identify this snapshot.'
    )
    name = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)
    container = models.ForeignKey('Container')

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


class GroupShare(models.Model):

    """
    Intermediate model to associate group's with shares.
    """

    group = models.ForeignKey(
        'BackendGroup',
        help_text='The group having access to the share.'
    )
    share = models.ForeignKey(
        'Share',
        help_text='The share the group has access to.'
    )

    class Meta:
        unique_together = ('group', 'share')


class Notification(models.Model):

    """
    Class that acts as a message between users and groups.
    """

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
    String to identify notifications for miscellaneous events.
    """
    MISCELLANEOUS = 'miscellaneous'

    """
    String to identify notifications for share related events.
    """
    SHARE = 'share'

    """
    List of choosable event event types.
    """
    EVENT_TYPES = [
        (CONTAINER, 'Container'),
        (GROUP, 'Group'),
        (IMAGE, 'Image'),
        (MISCELLANEOUS, 'Miscellaneous'),
        (SHARE, 'Share'),
    ]

    sender = models.ForeignKey(
        User,
        help_text='The user who send the notification.'
    )
    message = models.CharField(
        max_length=255,
        help_text='The message body.'
    )
    date = models.DateTimeField(default=datetime.now())
    event_type = models.CharField(
        choices=EVENT_TYPES,
        default=MISCELLANEOUS,
        max_length=20
    )
    related_object_id = models.IntegerField(
        blank=True,
        null=True,
        help_text='The id of the object related to the notification.'
    )

    def get_related_object(self):
        """
        Get the object related to by the notification.

        TODO: make this code more dynamic...
        """
        rel_id = self.related_object_id
        if not rel_id:
            return None

        if self.event_type == 'share':
            share = Share.objects.filter(id=rel_id)
            if share is not None:
                return share.first()
            else:
                return None
        elif self.event_type == 'container':
            container = Container.objects.filter(id=rel_id)
            if container is not None:
                return container.first()
            else:
                return None
        elif self.event_type == 'group':
            group = Group.objects.filter(id=rel_id)
            if group is not None:
                return group.first()
            else:
                return None
        elif self.event_type == 'image':
            image = ContainerImage.objects.filter(id=rel_id)
            if image is not None:
                return image.first()
            else:
                return None
        # return None per default
        return None

    def get_related_object_url_slug(self):
        """
        Todo: write doc.
        """
        obj = self.get_related_object()
        if obj is None:
            return None
        elif type(obj) is Share:
            # TODO: get url to share
            return "/share/manage/{}".format(obj.id)
        elif type(obj) is Container:
            # TODO: get url to container
            return "/containers/{}".format(obj.id)
        elif type(obj) is ContainerImage:
            # TODO: get url to image
            return "/images/{}".format(obj.id)
        elif type(obj) is Group:
            # TODO: get url to container
            return "/groups/manage/{}".format(obj.id)
        else:
            return None

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
    def for_user(cls, user):
        """
        TODO: document.
        """
        notifications = None
        try:
            notifications = NotificationLog.objects.filter(user=user.id).order_by("-notification__date")
        finally:
            return notifications

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode("@{0}: {1} (Read: {2})".format(
            self.user.__str__(),
            self.notification.__str__(),
            self.read
        ))

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
    receiving_group = models.ForeignKey(
        Group,
        help_text='The regular Django group that will receive this Notification.'
    )

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode("@{0}: {1}".format(
            self.receiving_group.__str__(),
            self.notification.__str__()
        ))

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()


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
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    owner = models.ForeignKey(
        'BackendUser',
        help_text='The user owning the share (usually the one that created it).'
    )
    group = models.OneToOneField(
        'BackendGroup',
        related_name='share',
        help_text='The (backend) group that is used to store membership information.'
    )

    def add_member(self, user):
        """
        Add the user as a member to this group.

        :param user: The user to add.
        """
        if self.user_is_member(user):
            return False
        self.group.django_group.user_set.add(user.django_user)
        return True

    # @classmethod
    # def all_user_is_member(cls, user):
    #     """
    #     Get all shares the user is a member of.
    #
    #     :param cls: The class on which the method was called.
    #     :param user: The user object to get the shares for.
    #     """
    #     shares = []
    #     for share in cls.objects.all():
    #         if share.is_member(user):
    #             shares.append(share)
    #     return shares

    def get_members(self):
        """
        Get a list of members for this share.
        """
        return [user.backend_user for user in self.group.django_group.user_set.all()]

    def remove_member(self, user):
        """
        Remove the member `user` from the group.

        :param user: The user to remove (if is member).

        :return bool `True` if the user has been a member and removed.
        """
        was_member = self.user_is_member(user)
        self.group.django_group.user_set.remove(user.django_user)
        return was_member

    def user_is_member(self, user):
        """
        Check if the user is a member of this share.

        :param user: The user to check for membership.
        """
        return user in self.get_members()

    # @classmethod
    # def for_user(cls, user):
    #     """
    #     TODO: document.
    #     """
    #     return cls.objects.filter(owner=user.id)

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
from ipynbsrv.core.signals import container_images, container_snapshots, \
    containers, group_shares, groups, shares, users
