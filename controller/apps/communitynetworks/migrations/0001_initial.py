# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import controller.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CnHost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_url', models.URLField(help_text=b"Optional URL pointing to a description of this host/device in its CN's node DB web application.", verbose_name=b'community network URL', blank=True)),
                ('cndb_uri', controller.models.fields.URIField(null=True, blank=True, help_text=b"Optional URI for this host/device in its CN's CNDB REST API", unique=True, verbose_name=b'community network database URI')),
                ('cndb_cached_on', models.DateTimeField(help_text=b'Last date that CNDB information for this host/device was successfully retrieved.', null=True, verbose_name=b'CNDB cached on', blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='cnhost',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
