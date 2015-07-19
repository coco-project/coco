from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.encoding import smart_unicode
from ipynbsrv.common.utils import ClassLoader
from ipynbsrv.contract.backends import ContainerBackend, SuspendableContainerBackend
from ipynbsrv.core import settings


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
    kind = models.CharField(choices=BACKEND_KINDS, default=CONTAINER_BACKEND, max_length=17, help_text='The kind of contract this backend fulfills.')
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

    It is used to create Django records for internal LDAP server groups so we can work
    with them like with any other Django objects, without having to worry about the fact that there's a server behind.
    """

    backend_id = models.PositiveIntegerField(unique=True, help_text='The ID for this group used internally by the backend.')
    backend_pk = models.CharField(unique=True, max_length=150, help_text='Unique identifier for this group used by the backend.')
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

    It is used to create Django records for internal LDAP server users so we can work
    with them like with any other Django objects, without having to worry about the fact that there's a server behind.
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
    The Container model is used to represent external container_backend instances.
    """

    id = models.AutoField(primary_key=True)
    backend_pk = models.CharField(max_length=255, help_text='The primary key the backend uses to identify this container.')
    name = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)
    server = models.ForeignKey('Server', help_text='The server on which this container is/will be located.')
    owner = models.ForeignKey('BackendUser')
    # ImageBasedContainerBackend
    image = models.ForeignKey('ContainerImage', blank=True, null=True, help_text='The image from which this container was bootstrapped.')
    # CloneableContainerBackend
    clone_of = models.ForeignKey('self', blank=True, null=True)

    def clone(self):
        """
        """
        self.server.get_container_backend_instance().clone_container(self.backend_pk, {})

    def create_snapshot(self, *args):
        """
        """
        self.server.get_container_backend_instance().create_container_snapshot(self.backend_pk, {})

    def delete_snapshot(self, snapshot, *args):
        """
        """
        self.server.get_container_backend_instance().delete_container_snapshot(self.backend_pk, snapshot.backend_pk)

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

    def get_backend_name(self):
        """
        Return the name of this container how it is named on the backend.
        """
        return "%s%i_%s" % (settings.CONTAINER_NAME_PREFIX, self.owner.backend_id, self.name)

    def get_friendly_name(self):
        """
        Return the humen-friendly name of this container.
        """
        return "%s-%s" % (self.owner.django_user.get_username(), self.name)

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
        """
        self.server.get_container_backend_instance().start_container(self.backend_pk, {})

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
    backend_pk = models.CharField(unique=True, max_length=255, help_text='The primary key the backend uses to identify this image.')
    name = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)
    # TODO: document placeholders
    command = models.CharField(max_length=255, blank=True, null=True, help_text='The command to execute inside the container upon start.')
    owner = models.ForeignKey(User)
    is_public = models.BooleanField(default=False)

    def get_backend_name(self):
        """
        Return the name of this image how it is named on the backend.
        """
        return "%s%i/%s" % (settings.CONTAINER_IMAGE_NAME_PREFIX, self.owner.backend_id, self.name)

    def get_friendly_name(self):
        """
        Return the humen-friendly name of this container.
        """
        if hasattr(self.owner, 'backend_user'):
            return "%s/%s" % (self.owner.get_username(), self.name)
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
    backend_pk = models.CharField(unique=True, max_length=255, help_text='The primary key the backend uses to identify this snapshot.')
    name = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)
    container = models.ForeignKey('Container')

    def get_full_name(self):
        """
        TODO: write doc.
        """
        # TODO: specification
        return '%s/%s' % (self.owner.get_username(), self.name)

    def restore(self):
        """
        """
        pass

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
        unique_together = ('name', 'container')


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
                                              Format: {'arg1': \"value\", 'arg2': \"value\"}""")

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
from ipynbsrv.core.signals import containers, \
    container_images, groups, users
