# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wui', '0002_auto_20141203_1137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='container',
            name='host',
        ),
        migrations.RemoveField(
            model_name='container',
            name='image',
        ),
        migrations.RemoveField(
            model_name='container',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='container',
            name='tags',
        ),
    ]
