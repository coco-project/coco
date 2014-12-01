# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wui', '0006_auto_20141201_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='docker_port',
            field=models.IntegerField(default=9999, max_length=6),
            preserve_default=True,
        ),
    ]
