# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wui', '0005_remove_host_ssh_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='docker_version',
            field=models.CharField(default='1.3.2', max_length=12),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='host',
            name='ssh_port',
            field=models.IntegerField(default=22),
            preserve_default=True,
        ),
    ]
