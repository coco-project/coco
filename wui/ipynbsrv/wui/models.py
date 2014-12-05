from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.encoding import smart_unicode
import ldapdb.models
from ldapdb.models.fields import (CharField, DateField, ImageField, ListField,
                                  IntegerField, FloatField)


class LdapGroup(ldapdb.models.Model):
    """
    Model for representing an LDAP group entry.
    """
    # LDAP meta-data
    base_dn = "ou=groups,dc=ipynbsrv,dc=ldap"
    object_classes = ['posixGroup']

    gid = IntegerField(db_column='gidNumber', unique=True)
    name = CharField(db_column='cn', max_length=200, primary_key=True)
    members = ListField(db_column='memberUid')

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
    """
    Model for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = "ou=users,dc=ipynbsrv,dc=ldap"
    object_classes = ['inetOrgPerson', 'posixAccount']

    # inetOrgPerson
    cn = CharField(db_column='cn', unique=True)
    sn = CharField(db_column='sn', unique=True)
    uid = IntegerField(db_column='uidNumber', unique=True)
    username = CharField(db_column='uid', max_length=200, primary_key=True)
    password = CharField(db_column='userPassword')
    group = IntegerField(db_column='gidNumber')
    home_directory = CharField(db_column='homeDirectory')

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
    """
    """
    label = models.CharField(primary_key=True, max_length=50)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return smart_unicode(self.label)


class Share(models.Model):
    """
    """
    name        = models.CharField(null=False, max_length=75)
    description = models.TextField(null=True, blank=True)
    tags        = models.ManyToManyField(Tag)
    owner       = models.ForeignKey(User)
    group       = models.ForeignKey(Group)

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
        return self.__unicode__()

    def __unicode__(self):
        return smart_unicode(self.name)


""
class Host(models.Model):
    ip             = models.CharField(primary_key=True, null=False, max_length=15)
    fqdn           = models.CharField(unique=True, null=True, blank=True, max_length=75)
    username       = models.CharField(null=False, max_length=30)
    ssh_port       = models.IntegerField(null=False, default=22)
    docker_version = models.CharField(null=False, max_length=12)
    docker_port    = models.IntegerField(null=False, max_length=6, default=9999)


"FIXME: PK should be img_id and host"
class Image(models.Model):
    id          = models.AutoField(primary_key=True)
    img_id      = models.CharField(null=False, max_length=12)
    cmd         = models.CharField(null=True, blank=True, max_length=100)
    ports       = models.CharField(null=True, blank=True, max_length=25)
    name        = models.CharField(null=False, max_length=75)
    description = models.TextField(null=True, blank=True)
#    host        = models.ForeignKey(Host)
#    owner       = models.ForeignKey(User)
#    tags        = models.ManyToManyField(Tag)
#    parent      = models.ForeignKey('self', null=True, blank=True)
    is_backup   = models.BooleanField(default=False)


"FIXME: PK should be ct_id and host"
class Container(models.Model):
    id          = models.AutoField(primary_key=True)
    ct_id       = models.CharField(null=False, max_length=12) # TODO: check default length
    name        = models.CharField(null=False, max_length=75)
    description = models.TextField(null=True, blank=True)
    status      = models.BooleanField(default=False)
    #host        = models.ForeignKey(Host)
    #image       = models.ForeignKey(Image)
    #owner       = models.ForeignKey(User)
    #tags        = models.ManyToManyField(Tag)

"FIXME: check either uid or gid, not both"
class ImageShare(models.Model):
    img_id = models.ForeignKey(Image)
    uid    = models.ForeignKey(User,  null=True, blank=True)
    gid    = models.ForeignKey(Group, null=True, blank=True)
    status = models.IntegerField(default='0', null=False) # 0: pending, 1: accepted, 2: declined
