from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.encoding import smart_unicode
from ipynbsrv.common.utils import ClassLoader
from ipynbsrv.contract.backends import ContainerBackend
from ipynbsrv.core import settings
from ipynbsrv.core.validators import validate_json_format
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
        validators=[
            RegexValidator(
                regex='^[a-z][A-z\d]+(\.[A-z\d]+)*$',
                message='Not a valid Python module path.'
            )
        ],
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
        validators=[validate_json_format],
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

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(Backend, self).save(*args, **kwargs)

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
    django_group = models.OneToOneField(
        Group,
        related_name='backend_group',
        help_text='The regular Django group this backend group is associated with.'
    )
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

    def add_member(self, user):
        """
        Add the user as a member to this group.

        :param user: The user to add.
        """
        if self.user_is_member(user):
            return False
        self.django_group.user_set.add(user.django_user)
        return True

    def clean_fields(self, exclude={}):
        """
        :inherit.
        """
        if not 'backend_id' in exclude and self.backend_id is None:
            self.backend_id = self.__class__.generate_internal_gid()
        super(BackendGroup, self).clean_fields(exclude)

    @staticmethod
    def generate_internal_gid():
        """
        Generate an unique internal group ID.

        Used for user-created groups. The primary group of each user should use the user's uid as guid.
        """
        last_django_id = 0
        if Group.objects.count() > 0:
            last_django_id = Group.objects.latest('id').id
        return settings.GROUP_ID_OFFSET + last_django_id

    def get_members(self):
        """
        Get a list of members for this group.
        """
        return [user.backend_user for user in self.django_group.user_set.all()]

    def remove_member(self, user):
        """
        Remove the member `user` from the group.

        :param user: The user to remove (if is member).

        :return bool `True` if the user has been a member and removed.
        """
        if self.user_is_member(user):
            self.django_group.user_set.remove(user.django_user)
            return True
        return False

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(BackendGroup, self).save(*args, **kwargs)

    def user_is_member(self, user):
        """
        Check if the user is a member of this group.

        :param user: The user to check for membership.
        """
        return user in self.get_members()

    def __str__(self):
        """
        :inherit.
        """
        return str(self.django_group)

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
    django_user = models.OneToOneField(
        User,
        related_name='backend_user',
        help_text='The regular Django user this backend user is associated with.'
    )
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
    primary_group = models.OneToOneField(
        'BackendGroup',
        related_name='primary_user',
        help_text='The primary backend group this user belongs to.'
    )

    def clean_fields(self, exclude={}):
        """
        :inherit.
        """
        if not 'backend_id' in exclude and self.backend_id is None:
            self.backend_id = self.__class__.generate_internal_uid()
        super(BackendUser, self).clean_fields(exclude)

    @staticmethod
    def generate_internal_uid():
        """
        Generate an unique internal user ID.
        """
        last_django_id = 0
        if BackendUser.objects.count() > 0:
            last_django_id = BackendUser.objects.latest('id').id
        return settings.USER_ID_OFFSET + last_django_id

    def get_username(self):
        """
        Get the user's internal username.
        """
        return self.django_user.get_username()

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(BackendUser, self).save(*args, **kwargs)

    def __str__(self):
        """
        :inherit.
        """
        return str(self.django_user)

    def __unicode__(self):
        """
        :inherit.
        """
        return self.__str__()


class CollaborationGroup(models.Model):

    """
    Collaboration groups can be created by users.
    """

    id = models.AutoField(primary_key=True)
    django_group = models.OneToOneField(
        Group,
        related_name='collaboration_group',
        help_text='The regular Django group this backend group is associated with.'
    )
    creator = models.ForeignKey(
        'BackendUser',
        blank=True,
        null=True,
        related_name='created_groups',
        help_text='The user that created the group.'
    )
    admins = models.ManyToManyField(
        'BackendUser',
        related_name='managed_groups',
        help_text='The users that are allowed to manage the group.'
    )
    is_public = models.BooleanField(
        default=False,
        help_text='Indicate if the group should be publicly visible and free to join for everyone.'
    )

    def add_admin(self, user):
        """
        Add the user as an administrator to this group.

        :param user: The backend user to add.
        """
        if self.user_is_member(user):
            return False
        self.admins.add(user)
        return True

    def add_member(self, user):
        """
        Add the user as a member to this group.

        :param user: The backend user to add.
        """
        if self.user_is_member(user):
            return False
        self.django_group.user_set.add(user.django_user)
        return True

    def get_members(self):
        """
        Get a list of members for this group.
        """
        return [user.backend_user for user in self.django_group.user_set.all()]

    def get_name(self):
        """
        Get the name of the collaboration group.
        """
        return self.django_group.name

    def get_member_count(self):
        """
        Get the number of users in the group.
        """
        return self.django_group.user_set.all().count()

    def remove_member(self, user):
        """
        Remove the member `user` from the group.

        :param user: The user to remove (if is member).

        :return bool `True` if the user has been a member and removed.
        """
        if self.user_is_member(user):
            self.django_group.user_set.remove(user.django_user)
            return True
        return False

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(CollaborationGroup, self).save(*args, **kwargs)

    def user_is_member(self, user):
        """
        Check if the backend user is a member of this group.

        :param user: The user to check for membership.
        """
        return user in self.get_members()

    def __str__(self):
        """
        :inherit.
        """
        return str(self.django_group)

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
    name = models.CharField(
        max_length=75,
        validators=[
            RegexValidator(
                regex='^[A-z]\w*$',
                message='Invalid container name.'
            )
        ]
    )
    description = models.TextField(blank=True, null=True)
    server = models.ForeignKey(
        'Server',
        related_name='containers',
        help_text='The server on which this container is/will be located.'
    )
    owner = models.ForeignKey(
        'BackendUser',
        related_name='containers',
        help_text='The user owning this container.'
    )
    image = models.ForeignKey(
        'ContainerImage',
        blank=True,
        null=True,
        related_name='containers',
        help_text='The image from which this container was bootstrapped.'
    )
    clone_of = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='base_for',
        help_text='The container on which this one is based/was cloned from.'
    )

    def clean(self):
        """
        :inherit.
        """
        if not self.image and not self.clone_of:
            raise ValidationError({
                'image': 'Either "image" or "clone_of" needs to be set.',
                'clone_of': 'Either "image" or "clone_of" needs to be set.'
            })
        super(Container, self).clean()

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
        container_cloned.send(sender=Container, container=self, clone=clone)

        return clone

    def commit(self, name, description=None, public=False):
        """
        Create a new container image based on the container.

        :param name: The name of the newly created container image.
        :param description: The optional description of the image.
        :param public: If `True`, the image will be public.
        """
        image = ContainerImage(
            name=name,
            description=description,
            command=self.image.command,
            protected_port=self.image.protected_port,
            public_ports=self.image.public_ports,
            owner=self.owner.django_user,
            is_public=public,
            is_internal=self.image.is_internal
        )
        image.save()

        from ipynbsrv.core.signals.signals import container_committed
        container_committed.send(sender=Container, container=self, image=image)

        return image

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
        Return the human-friendly name of this container.
        """
        return self.owner.django_user.get_username() + '_' + self.name

    def get_port_mappings(self, tuples=False):
        """
        Return the port mappings for this container.

        :param tuples: If `True`, tuples in the form (internal, exposed) are returned.
        """
        mappings = []
        reported_mappings = self.server.get_container_backend().get_container(self.backend_pk) \
                                .get(ContainerBackend.CONTAINER_KEY_PORT_MAPPINGS)
        if tuples:
            for reported_mapping in reported_mappings:
                mappings.append((
                    reported_mapping.get(ContainerBackend.PORT_MAPPING_KEY_INTERNAL),
                    reported_mapping.get(ContainerBackend.PORT_MAPPING_KEY_EXTERNAL)
                ))
        else:
            mappings = reported_mappings
        return mappings

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

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(Container, self).save(*args, **kwargs)

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
    protected_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="""The image\'s protected internal port.
        This port is only accessable through the ipynbsrv application for the container owner."""
    )
    public_ports = models.CommaSeparatedIntegerField(
        default='22',
        blank=True,
        null=True,
        max_length=75,
        help_text="""A comma-separated list of ports to expose to the public.
        In contrast to 'protected_port', nothing is done to protect access to those ports."""
    )
    owner = models.ForeignKey(
        User,
        related_name='container_images',
        help_text='The user owning this image. A system user should be taken for public images.'
    )
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

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(ContainerImage, self).save(*args, **kwargs)

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
    name = models.CharField(
        max_length=75,
        validators=[
            RegexValidator(
                regex='^[A-z]\w*$',
                message='Invalid container snapshot name.'
            )
        ]
    )
    description = models.TextField(blank=True, null=True)
    container = models.ForeignKey(
        'Container',
        related_name='snapshots',
        help_text='The container from which this snapshot was taken/is for.'
    )

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

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(ContainerSnapshot, self).save(*args, **kwargs)

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
    String to identify notifications for container related events.
    """
    CONTAINER = 'container'

    """
    String to identify notifications for container image related events.
    """
    CONTAINER_IMAGE = 'container_image'

    """
    String to identify notifications for group related events.
    """
    GROUP = 'group'

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
    NOTIFICATION_TYPES = [
        (CONTAINER, 'Container'),
        (CONTAINER_IMAGE, 'Container image'),
        (GROUP, 'Group'),
        (MISCELLANEOUS, 'Miscellaneous'),
        (SHARE, 'Share'),
    ]

    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        User,
        related_name='notifications',
        help_text='The user who sent the notification.'
    )
    message = models.CharField(
        max_length=255,
        help_text='The message body.'
    )
    date = models.DateTimeField(auto_now=True)
    notification_type = models.CharField(
        choices=NOTIFICATION_TYPES,
        default=MISCELLANEOUS,
        max_length=15
    )
    receiver_groups = models.ManyToManyField(
        'CollaborationGroup',
        related_name='notifications',
        help_text='The groups that receive that notification.'
    )
    # related objects
    container = models.ForeignKey(
        'Container',
        blank=True,
        null=True,
        related_name='related_notifications',
        help_text='The container this notification is related to.'
    )
    container_image = models.ForeignKey(
        'ContainerImage',
        blank=True,
        null=True,
        related_name='related_notifications',
        help_text='The container image this notification is related to.'
    )
    group = models.ForeignKey(
        'CollaborationGroup',
        blank=True,
        null=True,
        related_name='related_notifications',
        help_text='The group this notification is related to.'
    )
    share = models.ForeignKey(
        'Share',
        blank=True,
        null=True,
        related_name='related_notifications',
        help_text='The share this notification is related to.'
    )

    def clean(self):
        """
        :inherit.
        """
        if self.notification_type == 'container' and not self.container:
            raise ValidationError({
                'notification_type': 'Related container needed for this type.',
                'container': 'Related container must be choosen.'
            })
        elif self.notification_type == 'container_image':
            raise ValidationError({
                'notification_type': 'Related container image needed for this type.',
                'container_image': 'Related container image must be choosen.'
            })
        elif self.notification_type == 'group':
            raise ValidationError({
                'notification_type': 'Related group needed for this type.',
                'group': 'Related group must be choosen.'
            })
        elif self.notification_type == 'share':
            raise ValidationError({
                'notification_type': 'Related share needed for this type.',
                'share': 'Related share must be choosen.'
            })
        super(Notification, self).clean()

    def get_related_object(self):
        """
        Get the object related.
        """
        if self.container is not None:
            return self.container
        if self.container_image is not None:
            return self.container_image
        if self.group is not None:
            return self.group
        if self.share is not None:
            return self.share
        return None

    def has_related_object(self):
        """
        Check if the notification is related to an object.

        :return bool `True` if the notification has a related object.
        """
        return self.get_related_object() is not None

    # def get_related_object_url_slug(self):
    #     """
    #     Todo: write doc.
    #     """
    #     obj = self.get_related_object()
    #     if obj is None:
    #         return None
    #     elif type(obj) is Share:
    #         # TODO: get url to share
    #         return "/share/manage/{}".format(obj.id)
    #     elif type(obj) is Container:
    #         # TODO: get url to container
    #         return "/containers/{}".format(obj.id)
    #     elif type(obj) is ContainerImage:
    #         # TODO: get url to image
    #         return "/images/{}".format(obj.id)
    #     elif type(obj) is Group:
    #         # TODO: get url to container
    #         return "/groups/manage/{}".format(obj.id)
    #     else:
    #         return None

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(Notification, self).save(*args, **kwargs)

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode("%s: %s" % (self.date, self.message))

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
        'Notification',
        related_name='logs',
        help_text='The notification itself.'
    )
    user = models.ForeignKey(
        'BackendUser',
        related_name='notification_logs',
        help_text='The user assigned to this NotificationLog entry.'
    )
    read = models.BooleanField(default=False)

    # @classmethod
    # def for_user(cls, user):
    #     """
    #     TODO: document.
    #     """
    #     notifications = None
    #     try:
    #         notifications = NotificationLog.objects.filter(user=user.id).order_by("-notification__date")
    #     finally:
    #         return notifications

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(NotificationLog, self).save(*args, **kwargs)

    def __str__(self):
        """
        :inherit.
        """
        return smart_unicode("@%s: %s (Read: %b)" % (self.user, self.notification, self.read))

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
        limit_choices_to={'kind': Backend.CONTAINER_BACKEND},
        related_name='servers'
    )
    container_backend_args = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        validators=[validate_json_format],
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
                .replace('%internal_ip%', self.internal_ip) \
                .replace('%external_ip%', self.external_ip)
        return None

    def is_container_host(self):
        """
        Check if this server is configured as a container host (has a container_backend set).
        """
        return self.container_backend is not None

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(Server, self).save(*args, **kwargs)

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
    backend_group = models.OneToOneField(
        'BackendGroup',
        related_name='share',
        help_text='The (backend) group that is used to store membership information.'
    )
    name = models.CharField(
        unique=True,
        max_length=75,
        validators=[
            RegexValidator(
                regex='^[A-z]\w*$',
                message='Invalid share name.'
            )
        ]
    )
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(
        'BackendUser',
        related_name='shares',
        help_text='The user owning the share (usually the one that created it).'
    )
    access_groups = models.ManyToManyField(
        'CollaborationGroup',
        blank=True,
        related_name='shares',
        help_text='The groups having access to that share.'
    )
    tags = models.ManyToManyField('Tag', blank=True)

    def add_member(self, user):
        """
        Add the user as a member to this share.

        :param user: The user to add.
        """
        if self.user_is_member(user):
            return False
        self.backend_group.django_group.user_set.add(user.django_user)
        return True

    def get_members(self):
        """
        Get a list of members for this share.
        """
        return [user.backend_user for user in self.backend_group.django_group.user_set.all()]

    def remove_member(self, user):
        """
        Remove the member `user` from the share.

        :param user: The user to remove (if is member).

        :return bool `True` if the user has been a member and removed.
        """
        if self.user_is_member(user):
            self.backend_group.django_group.user_set.remove(user.django_user)
            return True
        return False

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(Share, self).save(*args, **kwargs)

    def user_is_member(self, user):
        """
        Check if the user is a member of this share.

        :param user: The user to check for membership.
        """
        return user in self.get_members()

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
    label = models.CharField(
        max_length=75,
        validators=[
            RegexValidator(
                regex='^[A-z]\w*$',
                message='Invalid label'
            )
        ]
    )

    def save(self, *args, **kwargs):
        """
        :inherit.
        """
        self.full_clean()
        super(Tag, self).save(*args, **kwargs)

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
from ipynbsrv.core.signals import backend_users, backend_groups, \
    collaboration_groups, container_images, container_snapshots, containers, \
    groups, notifications, shares, users
