import ldapdb.models
from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.encoding import smart_unicode
from ldapdb.models import fields
from ipynbsrv.wui.signals.signals import *
from random import randint


class Backend(models.Model):
    '''
    The backend model is used to store references to concrete backend implementations (as per ipynbsrv-contract package).

    Attn: The module/class needs to be installed manually. There's no magic involved for this.
    '''

    '''
    String to identify a backend of kind 'container backend'.
    '''
    CONTAINER_BACKEND = 'container_backend'

    '''
    List of pluggable backends.
    '''
    BACKEND_KINDS = [
        (CONTAINER_BACKEND, 'Container backend')
    ]

    id = models.AutoField(primary_key=True)
    kind = models.CharField(max_length=1, choices=BACKEND_KINDS, default=CONTAINER_BACKEND, help_text='The kind of contract this backend fulfills.')
    module = models.CharField(max_length=255, help_text='The full absolute module path.')
    klass = models.TextField(max_length=255, help_text='The class\' name under which it can be located within the module.')
    arguments = models.CharField(blank=True, null=True, max_length='255',
                                 help_text='Optional arguments to pass to the __init__ method of the class. Format: arg1=value,arg2=value')


class Server(models.Model):
    '''
    TODO: brief summary
    '''

    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255, help_text='The human-friendly name of this server.')
    hostname = models.CharField(unique=True, max_length=255)
    internal_ip = models.GenericIPAddressField(unique=True, protocol='IPv4', help_text='The IPv4 address of the internal ovsbr0 interface.')
    external_ip = models.GenericIPAddressField(unique=True, protocol='IPv4', help_text='The external IPv4 address of this server.')

    '''
    A reference to the backend to use as a container backend on this server.
    If this field is other than 'None', the server is considered a container host.
    '''
    container_backend = models.ForeignKey(Backend, blank=True, null=True, default=None)

    '''
    Checks if this server is configured as a container host (has a container_backend set).
    '''
    def is_container_host(self):
        return self.container_backend is not None


CONTAINER_CLONE_SUFFIX = '_clone'


class LdapGroup(ldapdb.models.Model):
    # LDAP meta-data
    base_dn = "ou=groups,dc=ipynbsrv,dc=ldap"  # TODO: get from settings
    object_classes = ['posixGroup']

    id = fields.IntegerField(db_column='gidNumber', unique=True)
    name = fields.CharField(db_column='cn', primary_key=True, max_length=200)
    members = fields.ListField(db_column='memberUid')

    def get_members(self):
        members = []
        for member in self.members:
            members.append(LdapUser.objects.get(pk=member))
        return members

    def is_member(self, user):
        return user in self.get_members()

    def __str__(self):
        return smart_unicode(self.name)

    def __unicode__(self):
        return self.__str__()


class LdapUser(ldapdb.models.Model):
    # LDAP meta-data
    base_dn = "ou=users,dc=ipynbsrv,dc=ldap"
    object_classes = ['inetOrgPerson', 'posixAccount']

    # inetOrgPerson
    cn = fields.CharField(db_column='cn', unique=True)
    sn = fields.CharField(db_column='sn', unique=True)
    id = fields.IntegerField(db_column='uidNumber', unique=True)
    username = fields.CharField(db_column='uid', primary_key=True, max_length=200)
    password = fields.CharField(db_column='userPassword')
    group_id = fields.IntegerField(db_column='gidNumber')
    home_directory = fields.CharField(db_column='homeDirectory', unique=True)

    @staticmethod
    def for_user(user):
        return LdapUser.objects.get(pk=user.username)

    def get_groups(self):
        groups = []
        for group in LdapGroup.objects.all():
            if group.is_member(self):
                groups.append(group)
        return groups

    def get_primary_group(self):
        return LdapGroup.objects.get(pk=self.pk)

    def get_username(self):
        return self.username

    def __str__(self):
        return smart_unicode(self.username)

    def __unicode__(self):
        return self.__str__()


class Tag(models.Model):
    label = models.CharField(primary_key=True, max_length=50)

    def __str__(self):
        return smart_unicode(self.label)

    def __unicode__(self):
        return self.__str__()


class Share(models.Model):
    name = models.CharField(unique=True, max_length=75)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    owner = models.ForeignKey(User)
    group = models.ForeignKey(Group, unique=True)

    @staticmethod
    def for_user(user):
        shares = []
        for share in Share.objects.all():
            if share.is_member(user):
                shares.append(share)
        return shares

    def get_members(self):
        return self.group.user_set.all()

    @staticmethod
    def get_unsynchonized_fields():
        # TODO: support these
        return ('name', 'owner', 'group')

    def is_member(self, user):
        return user in self.get_members()

    def __str__(self):
        return smart_unicode(self.name)

    def __unicode__(self):
        return self.__str__()


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    docker_id = models.CharField(unique=True, max_length=64)
    name = models.CharField(null=False, max_length=75)
    description = models.TextField(null=True, blank=True)
    cmd = models.CharField(null=True, blank=True, max_length=100)
    exposed_ports = models.CommaSeparatedIntegerField(null=True, blank=True, max_length=24)
    proxied_port = models.PositiveIntegerField(null=True, blank=True, max_length=6)
    owner = models.ForeignKey(User)
    is_public = models.BooleanField(default=False)
    is_clone = models.BooleanField(default=False)

    def get_full_name(self):
        return self.owner.get_username() + "/" + self.name

    @staticmethod
    def get_unsynchonized_fields():
        # TODO: support is_public changes
        return ('docker_id', 'is_public', 'is_clone')

    def __str__(self):
        return smart_unicode(self.get_full_name())

    def __unicode__(self):
        return self.__str__()

    class Meta:
        unique_together = ('name', 'owner')


class Container(models.Model):
    id = models.AutoField(primary_key=True)
    host = models.ForeignKey(Server)
    docker_id = models.CharField(unique=True, max_length=64)
    name = models.CharField(null=False, max_length=75)
    description = models.TextField(null=True, blank=True)
    image = models.ForeignKey(Image)
    owner = models.ForeignKey(User)
    running = models.BooleanField(default=False)
    clone_of = models.ForeignKey('self', null=True, blank=True, default=None)

    def clone(self):
        clone_name = self.name + CONTAINER_CLONE_SUFFIX
        clone_img_name = self.name + CONTAINER_CLONE_SUFFIX
        # if this is not the first clone, add count so names are unique
        existing_clones = Container.objects.filter(clone_of=self)
        if existing_clones.exists():
            num_clones = len(existing_clones) + 1
            clone_name += '_%d' % num_clones
            clone_img_name += '_%d' % num_clones

        img = self.commit(img_name=clone_img_name, description=self.image.description, public=False, clone=True)
        clone = Container(id=randint(0, 1000), name=clone_name, description=self.description, image=img,
                          owner=self.owner, running=False, clone_of=self)
        container_cloned.send(sender=Container, container=self, clone=clone)
        clone.save()

        if self.running:
            clone.start()
        else:
            clone.stop()

        return clone

    def commit(self, img_name, description, public, clone=False):
        image = Image(id=randint(0, 1000), name=img_name, description=description, cmd=self.image.cmd, exposed_ports=self.image.exposed_ports,
                      proxied_port=self.image.proxied_port, owner=self.owner, is_public=public, is_clone=clone)
        container_commited.send(sender=Container, container=self, image=image)
        image.save()

        return image

    def get_full_name(self):
        return self.owner.get_username() + "_" + self.name

    @staticmethod
    def get_unsynchonized_fields():
        # TODO: support name and running changes
        return ('docker_id', 'name', 'image', 'owner', 'running', 'clone_of')

    def has_clones(self):
        return Container.objects.filter(clone_of=self).exists()

    def restart(self):
        self.running = True
        self.save(update_fields=['running'])
        container_restarted.send(sender=Container, container=self)

    def start(self):
        self.running = True
        self.save(update_fields=['running'])
        container_started.send(sender=Container, container=self)

    def stop(self):
        self.running = False
        self.save(update_fields=['running'])
        container_stopped.send(sender=Container, container=self)

    def __str__(self):
        return smart_unicode(self.get_full_name())

    def __unicode__(self):
        return self.__str__()

    class Meta:
        unique_together = ('name', 'owner')


class PortMapping(models.Model):
    container = models.ForeignKey(Container)
    internal = models.PositiveIntegerField(null=False, max_length=6)
    external = models.PositiveIntegerField(unique=True, max_length=6)

    @staticmethod
    def get_unsynchonized_fields():
        return ('container', 'internal', 'external')

    def __str__(self):
        return smart_unicode("%s: %i -> %i" % (self.container.name, self.internal, self.external))

    def __unicode__(self):
        return self.__str__()

    class Meta:
        get_latest_by = 'external'
        order_with_respect_to = 'container'
        unique_together = ('container', 'internal')
