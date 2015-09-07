# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snippetalk', '0013_comment_level'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='level',
        ),
    ]
