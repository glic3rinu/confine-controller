# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('samples', models.PositiveIntegerField(default=4)),
                ('packet_loss', models.PositiveIntegerField(null=True)),
                ('min', models.DecimalField(null=True, verbose_name=b'RTT min', max_digits=9, decimal_places=3)),
                ('avg', models.DecimalField(null=True, verbose_name=b'RTT avg', max_digits=9, decimal_places=3)),
                ('max', models.DecimalField(null=True, verbose_name=b'RTT max', max_digits=9, decimal_places=3)),
                ('mdev', models.DecimalField(null=True, verbose_name=b'RTT mdev', max_digits=9, decimal_places=3)),
                ('date', models.DateTimeField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'get_latest_by': 'date',
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='ping',
            index_together=set([('object_id', 'content_type', 'date')]),
        ),
    ]
