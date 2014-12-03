# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wui', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='system',
        ),
        migrations.RemoveField(
            model_name='host',
            name='ssh_priv_key',
        ),
        migrations.RemoveField(
            model_name='host',
            name='ssh_pub_key',
        ),
        migrations.AddField(
            model_name='group',
            name='is_system',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='is_backup',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='parent',
            field=models.ForeignKey(blank=True, to='wui.Image', null=True),
            preserve_default=True,
        ),
    ]
