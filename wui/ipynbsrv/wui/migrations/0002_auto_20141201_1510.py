# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wui', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='container',
            name='description',
            field=models.TextField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='ssh_priv_key',
            field=models.TextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='ssh_pub_key',
            field=models.TextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='image',
            name='description',
            field=models.TextField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='share',
            name='description',
            field=models.TextField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
