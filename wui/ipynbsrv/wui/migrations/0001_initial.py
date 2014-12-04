# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('ct_id', models.CharField(max_length=12)),
                ('name', models.CharField(max_length=75)),
                ('description', models.TextField(null=True, blank=True)),
                ('status', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('ip', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('fqdn', models.CharField(max_length=75, unique=True, null=True, blank=True)),
                ('username', models.CharField(max_length=30)),
                ('ssh_port', models.IntegerField(default=22)),
                ('docker_version', models.CharField(max_length=12)),
                ('docker_port', models.IntegerField(default=9999, max_length=6)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('img_id', models.CharField(max_length=12)),
                ('cmd', models.CharField(max_length=100, null=True, blank=True)),
                ('ports', models.CharField(max_length=25, null=True, blank=True)),
                ('name', models.CharField(max_length=75)),
                ('description', models.TextField(null=True, blank=True)),
                ('is_backup', models.BooleanField(default=False)),
                ('host', models.ForeignKey(to='wui.Host')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, to='wui.Image', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageShare',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=b'0')),
                ('gid', models.ForeignKey(blank=True, to='auth.Group', null=True)),
                ('img_id', models.ForeignKey(to='wui.Image')),
                ('uid', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LdapGroup',
            fields=[
                ('dn', models.CharField(max_length=200)),
                ('gid', ldapdb.models.fields.IntegerField(unique=True, db_column=b'gidNumber')),
                ('name', ldapdb.models.fields.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'cn')),
                ('members', ldapdb.models.fields.ListField(db_column=b'memberUid')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LdapUser',
            fields=[
                ('dn', models.CharField(max_length=200)),
                ('uid', ldapdb.models.fields.IntegerField(unique=True, db_column=b'uidNumber')),
                ('group', ldapdb.models.fields.IntegerField(db_column=b'gidNumber')),
                ('home_directory', ldapdb.models.fields.CharField(max_length=200, db_column=b'homeDirectory')),
                ('username', ldapdb.models.fields.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'uid')),
                ('password', ldapdb.models.fields.CharField(max_length=200, db_column=b'userPassword')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Share',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=75)),
                ('description', models.TextField(null=True, blank=True)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('label', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='share',
            name='tags',
            field=models.ManyToManyField(to='wui.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='tags',
            field=models.ManyToManyField(to='wui.Tag'),
            preserve_default=True,
        ),
    ]
