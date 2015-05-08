# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delivered',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('is_valid', models.BooleanField(default=True, help_text=b'Indicates whether the notification is still valid. Used in order to avoid repeated notifications when the condition is still valid')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=False)),
                ('label', models.CharField(unique=True, max_length=128, blank=True)),
                ('module', models.CharField(max_length=256, blank=True)),
                ('subject', models.CharField(max_length=256)),
                ('message', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='delivered',
            name='notification',
            field=models.ForeignKey(related_name='delivered', to='notifications.Notification'),
            preserve_default=True,
        ),
    ]
