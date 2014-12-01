# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wui', '0004_auto_20141201_1525'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='host',
            name='ssh_port',
        ),
    ]
