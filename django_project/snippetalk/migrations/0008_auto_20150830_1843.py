# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snippetalk', '0007_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snippet',
            name='public',
            field=models.IntegerField(default=True, choices=[(1, 'Public'), (0, 'Private')], verbose_name='Publicity'),
            preserve_default=True,
        ),
    ]
