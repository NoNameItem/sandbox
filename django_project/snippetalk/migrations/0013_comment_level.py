# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snippetalk', '0012_auto_20150905_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='level',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
