# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snippetalk', '0005_snippet_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snippet',
            name='public',
            field=models.BooleanField(default=True, choices=[(True, 'Public'), (False, 'Private')], verbose_name='Publicity'),
            preserve_default=True,
        ),
    ]
