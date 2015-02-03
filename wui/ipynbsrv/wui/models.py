from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.encoding import smart_unicode
import ldapdb.models
from ldapdb.models import fields


class LdapGroup(ldapdb.models.Model):
    # LDAP meta-data
    base_dn = "ou=groups,dc=ipynbsrv,dc=ldap"
    object_classes = ['posixGroup']

    gid = fields.IntegerField(db_column='gidNumber', unique=True)
    name = fields.CharField(db_column='cn', max_length=200, primary_key=True)
    members = fields.ListField(db_column='memberUid')

    def get_members(self):
        members = []
        for member_uid in self.members:
            members.append(LdapUser.objects.get(pk=member_uid))
        return members

    def is_member(self, user):
        return user in self.get_members()

    def __str__(self):
        return smart_unicode(self.name)

    def __unicode__(self):
        return smart_unicode(self.name)


class LdapUser(ldapdb.models.Model):
    # LDAP meta-data
    base_dn = "ou=users,dc=ipynbsrv,dc=ldap"
    object_classes = ['inetOrgPerson', 'posixAccount']

    # inetOrgPerson
    cn = fields.CharField(db_column='cn', unique=True)
    sn = fields.CharField(db_column='sn', unique=True)
    uid = fields.IntegerField(db_column='uidNumber', unique=True)
    username = fields.CharField(db_column='uid', max_length=200, primary_key=True)
    password = fields.CharField(db_column='userPassword')
    group = fields.IntegerField(db_column='gidNumber')
    home_directory = fields.CharField(db_column='homeDirectory')

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
        return smart_unicode(self.username)


class Tag(models.Model):
    label = models.CharField(primary_key=True, max_length=50)

    def __str__(self):
        return smart_unicode(self.label)

    def __unicode__(self):
        return smart_unicode(self.label)


class Share(models.Model):
    name = models.CharField(null=False, max_length=75)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    owner = models.ForeignKey(User)
    group = models.ForeignKey(Group)

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
        return smart_unicode(self.name)


# FIXME: PK should be img_id and host
class Image(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, max_length=75)
    description = models.TextField(null=True, blank=True)
    docker_id = models.CharField(null=False, max_length=64)
    cmd = models.CharField(null=True, blank=True, max_length=100)
    exposed_ports = models.CommaSeparatedIntegerField(null=True, blank=True, max_length=24)
    proxied_port = models.PositiveIntegerField(null=False, max_length=6)
    owner = models.ForeignKey(User)
    is_public = models.BooleanField(default=False)
    is_clone = models.BooleanField(default=False)

    def __str__(self):
        return smart_unicode(self.name)

    def __unicode__(self):
        return smart_unicode(self.name)


# FIXME: PK should be ct_id and host
class Container(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, max_length=75)
    description = models.TextField(null=True, blank=True)
    docker_id = models.CharField(null=False, max_length=64)
    image = models.ForeignKey(Image)
    owner = models.ForeignKey(User)
    running = models.BooleanField(default=False)
    clone_of = models.ForeignKey('self')

    def __str__(self):
        return smart_unicode(self.name)

    def __unicode__(self):
        return smart_unicode(self.name)
