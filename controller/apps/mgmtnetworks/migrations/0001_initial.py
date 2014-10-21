# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MgmtNetConf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('backend', models.CharField(default=b'tinc', help_text=b'The network backend that provides access to the management network.', max_length=16, verbose_name=b'Backend', choices=[(b'tinc', b'tinc'), (b'native', b'native')])),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='mgmtnetconf',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
