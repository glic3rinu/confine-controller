# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSerie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('value', jsonfield.fields.JSONField()),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'get_latest_by': 'date',
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='timeserie',
            index_together=set([('name', 'date')]),
        ),
    ]
