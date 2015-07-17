# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('topic', models.CharField(max_length=255, blank=True)),
                ('last_message_time', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('last_message_sender', models.ForeignKey(null=True, related_name='last_sender', to=settings.AUTH_USER_MODEL)),
                ('participants', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('datetime', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('thread', models.ForeignKey(to='chat.Chat')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
