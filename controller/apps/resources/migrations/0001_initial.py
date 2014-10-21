# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('object_id', models.PositiveIntegerField()),
                ('max_req', models.PositiveIntegerField(null=True, verbose_name=b'Max per sliver', blank=True)),
                ('dflt_req', models.PositiveIntegerField(verbose_name=b'Sliver default')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceReq',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('object_id', models.PositiveIntegerField()),
                ('req', models.PositiveIntegerField(null=True, verbose_name=b'Amount', blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Resource request',
                'verbose_name_plural': 'Resource requests',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='resource',
            unique_together=set([('name', 'object_id', 'content_type')]),
        ),
    ]
