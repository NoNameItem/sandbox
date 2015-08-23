# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snippetalk', '0004_auto_20150823_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='snippet',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
