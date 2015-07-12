from django.db import models
from django.utils.encoding import smart_unicode
from ipynbsrv.common.utils import ClassLoader
from ipynbsrv.contract.backends import ContainerBackend, SuspendableContainerBackend
from django.contrib.auth.models import Group, User


class Backend(models.Model):
    '''
    The backend model is used to store references to concrete backend implementations
    (as per ipynbsrv-contract package).

    Attn: The module/class needs to be installed manually. There's no magic included for this.
    '''

    '''
    String to identify a backend of kind 'container backend'.
    '''
    CONTAINER_BACKEND = 'container_backend'

    '''
    List of pluggable backends.
    '''
    BACKEND_KINDS = [
        (CONTAINER_BACKEND, 'Container backend'),
    ]

    id = models.AutoField(primary_key=True)
    kind = models.CharField(choices=BACKEND_KINDS, default=CONTAINER_BACKEND, max_length=17,
                            help_text='The kind of contract this backend fulfills.')
    module = models.CharField(max_length=255, help_text='The full absolute module path. (i.e. ipynbsrv.backends.container_backends)')
    klass = models.CharField(max_length=255, help_text='The class\' name under which it can be located within the module. (i.e. Docker or HttpRemote')
    arguments = models.CharField(blank=True, null=True, max_length=255,
                                 help_text='Optional arguments to pass to the __init__ method of the class. Format: {"arg1": "value", "arg2": "value" }')

    '''
    Returns an instance of the backend with either the default arguments
    or the one provided as an argument.

    :param arguments: If defined, use these arguments when calling the __init__ method.
    '''
    def get_instance(self, arguments=None):
        cl = ClassLoader(self.module, self.klass, self.arguments)
        return cl.get_instance(arguments)

    def __str__(self):
        return smart_unicode('%s.%s(%s)' % (self.module, self.klass, self.arguments))

    def __unicode__(self):
        return self.__str__()

    class Meta:
        unique_together = ('module', 'klass', 'arguments')


class Container(models.Model):
    '''
    TODO: brief summary
    '''

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
        raise NotImplementedError

    def create_snapshot(self, *args):
        raise NotImplementedError

    def delete_snapshot(self, *args):
        raise NotImplemented

    '''
    Returns the representation of this container as returned by the server's container backend instance.
    '''
    def get_server_backend_representation(self):
        return self.server.get_container_backend_instance().get_container(self.backend_pk)

    '''
    Returns all containers that are clones of the one this method is called on.
    '''
    def get_clones(self):
        return Container.objects.filter(clone_of=self)

    '''
    Returns the full name (as it is named on the server's container backend) of this container.
    '''
    def get_full_name(self):
        # TODO: write specification
        return '%s_%s' % (self.owner.get_username(), self.name)

    '''
    Returns true if clones of this container exist, false otherwise.
    '''
    def has_clones(self):
        return Container.objects.filter(clone_of=self).exists()

    '''
    Returns true if this container is a clone of another one.
    '''
    def is_clone(self):
        return self.clone_of is not None

    '''
    Returns true if the container is running, false otherwise.
    '''
    def is_running(self):
        container = self.get_server_backend_representation()
        return ContainerBackend.STATUS_RUNNING == container.get('status')

    '''
    Returns true if the container is suspended, false otherwise.
    '''
    def is_suspended(self):
        container = self.get_server_backend_representation()
        return SuspendableContainerBackend.STATUS_SUSPENDED == container.get('status')

    '''
    Restarts the container.
    '''
    def restart(self):
        self.server.get_container_backend_instance().restart_container(self.backend_pk)

    '''
    Resumes the container.
    '''
    def resume(self):
        self.server.get_container_backend_instance().resume_container(self.backend_pk)

    def start(self, *args):
        raise NotImplementedError

    '''
    Stops the container.
    '''
    def stop(self):
        self.server.get_container_backend_instance().stop_container(self.backend_pk)

    '''
    Suspends the container.
    '''
    def suspend(self):
        self.server.get_container_backend_instance().suspend_container(self.backend_pk)

    def __str__(self):
        return smart_unicode(self.get_full_name())

    def __unicode__(self):
        return self.__str__()

    class Meta:
        unique_together = (
            ('backend_pk', 'server'),
            ('name', 'owner')
        )


class Image(models.Model):
    '''
    TODO: brief summary
    '''

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
        # TODO: specification
        return '%s/%s' % (self.owner.get_username(), self.name)

    '''
    Returns true if this image is a container snapshot.
    '''
    def is_snapshot(self):
        return self.snapshot_of is not None

    def __str__(self):
        return smart_unicode(self.get_full_name())

    def __unicode__(self):
        return self.__str__()

    class Meta:
        unique_together = ('name', 'owner')


class Server(models.Model):
    '''
    TODO: brief summary
    '''

    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255, help_text='The human-friendly name of this server.')
    hostname = models.CharField(unique=True, max_length=255)
    internal_ip = models.GenericIPAddressField(unique=True, protocol='IPv4',
                                               help_text='The IPv4 address of the internal ovsbr0 interface.')
    external_ip = models.GenericIPAddressField(unique=True, protocol='IPv4',
                                               help_text='The external IPv4 address of this server.')

    '''
    A reference to the backend to use as a container backend on this server.
    If this field is other than 'None', the server is considered a container host.
    '''
    container_backend = models.ForeignKey('Backend', blank=True, null=True, default=None,
                                          limit_choices_to={'kind': Backend.CONTAINER_BACKEND})
    container_backend_args = models.CharField(max_length=255, blank=True, null=True,
                                              help_text='''Optional arguments to pass to the backend\'s get_instance method.
                                              Available placeholders: all model fields in the form: %field_name%, e.g. %hostname%.
                                              Format: arg1=value,arg2=value''')

    '''
    Returns an instance of the container backend this server is using.
    '''
    def get_container_backend_instance(self):
        return self.backend.get_instance(self._get_interpolated_container_backend_args())

    '''
    Returns the container_backend_args value with placeholders/variables replaced
    with their actual value.
    '''
    def _get_interpolated_container_backend_args(self):
        if self.container_backend_args:
            # TODO: line breaks
            return self.container_backend_args.replace('%name%', self.name).replace('%hostname%', self.hostname).replace('%internal_ip%', self.internal_ip).replace('%external_ip%', self.external_ip)
        return None

    '''
    Checks if this server is configured as a container host (has a container_backend set).
    '''
    def is_container_host(self):
        return self.container_backend is not None

    def __str__(self):
        return smart_unicode(self.name)

    def __unicode__(self):
        return self.__str__()


class PortMapping(models.Model):
    container = models.ForeignKey(Container)
    internal = models.PositiveIntegerField(null=False, max_length=6)
    external = models.PositiveIntegerField(unique=True, max_length=6)

    def __str__(self):
        return smart_unicode("{0} ({1} -> {2})".format(self.container.__str__, self.external, self.internal))

    def __unicode__(self):
        return self.__str__()


class Share(models.Model):
    '''
    TODO: brief summary
    '''

    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=75)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField('Tag', null=True, blank=True)
    owner = models.ForeignKey(User)
    group = models.ForeignKey(Group, unique=True)

    '''
    Adds the user as a member to this group.

    :param user: The user to add.
    '''
    def add_member(self, user):
        if self.user_is_member(user):
            return False
        raise NotImplementedError

    '''
    Returns all shares the user is a member of.

    :param cls: The class on which the method was called.
    :param user: The user object to get the shares for.
    '''
    @classmethod
    def all_user_is_member(cls, user):
        shares = []
        for share in cls.objects.all():
            if share.is_member(user):
                shares.append(share)
        return shares

    '''
    Returns a list of members for this share.
    '''
    def get_members(self):
        return self.group.user_set.all()

    '''
    Removes the member 'user' from this group.

    :param user: The member to remove.
    '''
    def remove_member(self, user):
        # if not self.user_is_member(user):
        #     raise LogicError("User is not a member of the share.")
        raise NotImplementedError

    '''
    Checks if the user is a member of this share.

    :param user: The user to check for membership.
    '''
    def user_is_member(self, user):
        return user in self.get_members()

    def __str__(self):
        return smart_unicode(self.name)

    def __unicode__(self):
        return self.__str__()


class Tag(models.Model):
    '''
    TODO: brief summary
    '''

    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=75)

    def __str__(self):
        return smart_unicode(self.label)

    def __unicode__(self):
        return self.__str__()


class IpynbUser(models.Model):
    user = models.OneToOneField(User)
    identifier = models.CharField(max_length=75, unique=True, help_text='Unique identifier in usergroup backend')
    home_directory = models.CharField(max_length=255, unique=True, help_text='Home directory of the user to store data')
    additional_data = models.CharField(max_length=255, help_text='Here you can add any additional information that may be needed for your Usergroup Backend')

    def __str__(self):
        return smart_unicode(self.identifier)

    def __unicode__(self):
        return self.__str__()


class IpynbGroup(models.Model):
    group = models.OneToOneField(Group)
    identifier = models.CharField(max_length=75, unique=True, help_text='Unique identifier in usergroup backend')
    additional_data = models.CharField(max_length=255, help_text='Here you can add any additional information that may be needed for your Usergroup Backend')

    def __str__(self):
        return smart_unicode(self.identifier)

    def __unicode__(self):
        return self.__str__()
