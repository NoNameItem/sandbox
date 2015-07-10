# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_project', '0004_auto_20150709_1242'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='birth_date',
        ),
    ]
