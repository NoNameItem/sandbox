# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snippetalk', '0011_auto_20150905_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(null=True, to='snippetalk.Comment', related_name='answers', default=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='to_snippet',
            field=models.ForeignKey(default=0, related_name='comments', to='snippetalk.Snippet'),
            preserve_default=False,
        ),
    ]
