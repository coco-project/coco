from django.db import models


""
class User(models.Model):
    uid      = models.IntegerField(primary_key=True, max_length=10)
    username = models.CharField(null=False, blank=False, max_length=50)


""
class Group(models.Model):
    gid       = models.IntegerField(primary_key=True, max_length=10)
    groupname = models.CharField(null=False, blank=False, max_length=100)
    is_system = models.BooleanField(default=True)


""
class Tag(models.Model):
    label = models.CharField(primary_key=True, null=False, max_length=50)


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
    host        = models.ForeignKey(Host)
    owner       = models.ForeignKey(User)
    tags        = models.ManyToManyField(Tag)
    parent      = models.ForeignKey('self', null=True, blank=True)
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


""
class Share(models.Model):
    name        = models.CharField(primary_key=True, null=False, max_length=75)
    description = models.TextField(null=True, blank=True)
    owner       = models.ForeignKey(User)
    group       = models.ForeignKey(Group)
    tags        = models.ManyToManyField(Tag)


"FIXME: check either uid or gid, not both"
class ImageShare(models.Model):
    img_id = models.ForeignKey(Image)
    uid    = models.ForeignKey(User,  null=True, blank=True)
    gid    = models.ForeignKey(Group, null=True, blank=True)
