import ldapdb.models
from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.encoding import smart_unicode
from ldapdb.models import fields


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

    def is_member(self, user):
        return user in self.get_members()

    def __str__(self):
        return smart_unicode(self.name)

    def __unicode__(self):
        return self.__str__()


class Image(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    name = models.CharField(unique=True, null=False, max_length=75)
    description = models.TextField(null=True, blank=True)
    cmd = models.CharField(null=True, blank=True, max_length=100)
    exposed_ports = models.CommaSeparatedIntegerField(null=True, blank=True, max_length=24)
    proxied_port = models.PositiveIntegerField(null=True, blank=True, max_length=6)
    owner = models.ForeignKey(User)
    is_public = models.BooleanField(default=False)
    is_clone = models.BooleanField(default=False)

    def __str__(self):
        return smart_unicode(self.name)

    def __unicode__(self):
        return self.__str__()


class Container(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    name = models.CharField(unique=True, null=False, max_length=75)
    description = models.TextField(null=True, blank=True)
    image = models.ForeignKey(Image)
    owner = models.ForeignKey(User)
    running = models.BooleanField(default=False)
    clone_of = models.ForeignKey('self')

    def __str__(self):
        return smart_unicode(self.name)

    def __unicode__(self):
        return self.__str__()


class PortMapping(models.Model):
    container = models.ForeignKey(Container)
    internal = models.PositiveIntegerField(null=False, max_length=6)
    external = models.PositiveIntegerField(unique=True, max_length=6)

    def __str__(self):
        return smart_unicode("%s: %i -> %i" % self.container.name, self.internal, self.external)

    def __unicode__(self):
        return self.__str__()

    class Meta:
        get_latest_by = 'external'
        order_with_respect_to = 'container'
        unique_together = ('container', 'internal')
