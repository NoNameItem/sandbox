# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snippetalk', '0008_auto_20150830_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snippet',
            name='public',
            field=models.IntegerField(default=True, verbose_name='Publicity', choices=[(1, 'Public'), (2, 'Private')]),
            preserve_default=True,
        ),
    ]
