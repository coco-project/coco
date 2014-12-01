# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
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
            name='Group',
            fields=[
                ('gid', models.IntegerField(max_length=10, serialize=False, primary_key=True)),
                ('groupname', models.CharField(max_length=100)),
                ('system', models.BooleanField(default=True)),
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
                ('ssh_pub_key', models.TextField()),
                ('ssh_priv_key', models.TextField()),
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
                ('host', models.ForeignKey(to='wui.Host')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageShare',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gid', models.ForeignKey(blank=True, to='wui.Group', null=True)),
                ('img_id', models.ForeignKey(to='wui.Image')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Share',
            fields=[
                ('name', models.CharField(max_length=75, serialize=False, primary_key=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('group', models.ForeignKey(to='wui.Group')),
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
        migrations.CreateModel(
            name='User',
            fields=[
                ('uid', models.IntegerField(max_length=10, serialize=False, primary_key=True)),
                ('username', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='share',
            name='owner',
            field=models.ForeignKey(to='wui.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='share',
            name='tags',
            field=models.ManyToManyField(to='wui.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='imageshare',
            name='uid',
            field=models.ForeignKey(blank=True, to='wui.User', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='owner',
            field=models.ForeignKey(to='wui.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='tags',
            field=models.ManyToManyField(to='wui.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='container',
            name='host',
            field=models.ForeignKey(to='wui.Host'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='container',
            name='image',
            field=models.ForeignKey(to='wui.Image'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='container',
            name='owner',
            field=models.ForeignKey(to='wui.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='container',
            name='tags',
            field=models.ManyToManyField(to='wui.Tag'),
            preserve_default=True,
        ),
    ]
