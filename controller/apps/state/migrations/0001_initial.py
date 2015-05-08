# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NodeSoftwareVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=256)),
                ('node', models.OneToOneField(related_name='soft_version', to='nodes.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('last_seen_on', models.DateTimeField(help_text=b'Last time the state retrieval was successfull.', null=True)),
                ('last_try_on', models.DateTimeField(help_text=b'Last time the state retrieval operation has been executed.', null=True)),
                ('last_contact_on', models.DateTimeField(help_text=b'Last API pull of this resource received from the node.', null=True)),
                ('value', models.CharField(max_length=32, choices=[(b'started', b'STARTED'), (b'safe', b'SAFE'), (b'fail_allocate', b'FAIL_ALLOCATE'), (b'offline', b'OFFLINE'), (b'fail_start', b'FAIL_START'), (b'registered', b'REGISTERED'), (b'unknown', b'UNKNOWN'), (b'crashed', b'CRASHED'), (b'debug', b'DEBUG'), (b'production', b'PRODUCTION'), (b'fail_deploy', b'FAIL_DEPLOY'), (b'deployed', b'DEPLOYED'), (b'failure', b'FAILURE'), (b'nodata', b'NODATA')])),
                ('metadata', models.TextField()),
                ('data', models.TextField()),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('ssl_verified', models.BooleanField(default=False, help_text=b'Whether the SSL certificate could be verified on node API retrieval.', verbose_name=b'verified')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StateHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=32, choices=[(b'started', b'STARTED'), (b'safe', b'SAFE'), (b'fail_allocate', b'FAIL_ALLOCATE'), (b'offline', b'OFFLINE'), (b'fail_start', b'FAIL_START'), (b'registered', b'REGISTERED'), (b'unknown', b'UNKNOWN'), (b'crashed', b'CRASHED'), (b'debug', b'DEBUG'), (b'production', b'PRODUCTION'), (b'fail_deploy', b'FAIL_DEPLOY'), (b'deployed', b'DEPLOYED'), (b'failure', b'FAILURE'), (b'nodata', b'NODATA')])),
                ('start', models.DateTimeField(db_index=True)),
                ('end', models.DateTimeField()),
                ('data', models.TextField(default=b'', blank=True)),
                ('metadata', models.TextField(default=b'', blank=True)),
                ('state', models.ForeignKey(related_name='history', to='state.State')),
            ],
            options={
                'ordering': ('-start',),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
