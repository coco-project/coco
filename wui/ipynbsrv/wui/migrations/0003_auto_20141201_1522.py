# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wui', '0002_auto_20141201_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='ssh_port',
            field=models.CharField(max_length=12),
            preserve_default=True,
        ),
    ]
