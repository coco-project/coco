# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wui', '0003_auto_20141201_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='ssh_port',
            field=models.IntegerField(default=22),
            preserve_default=True,
        ),
    ]
