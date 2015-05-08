# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Execution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('script', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('retry_if_offline', models.BooleanField(default=True, help_text=b'The operation will be retried if the node is currently offline.')),
                ('include_new_nodes', models.BooleanField(default=False, help_text=b'If selected the operation will be executed on newly created nodes')),
            ],
            options={
                'ordering': ['-created_on'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(default=b'RECEIVED', max_length=16, choices=[(b'RECEIVED', b'RECEIVED'), (b'TIMEOUT', b'TIMEOUT'), (b'STARTED', b'STARTED'), (b'SUCCESS', b'SUCCESS'), (b'FAILURE', b'FAILURE'), (b'ERROR', b'ERROR'), (b'REVOKED', b'REVOKED'), (b'OUTDATED', b'OUTDATED')])),
                ('last_try', models.DateTimeField(null=True)),
                ('stdout', models.TextField()),
                ('stderr', models.TextField()),
                ('traceback', models.TextField()),
                ('exit_code', models.IntegerField(null=True)),
                ('task_id', models.CharField(help_text=b'Celery task ID', max_length=36, unique=True, null=True)),
                ('execution', models.ForeignKey(related_name='instances', to='maintenance.Execution')),
                ('node', models.ForeignKey(related_name='operations', to='nodes.Node')),
            ],
            options={
                'ordering': ['-last_try'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Verbose name', max_length=256)),
                ('identifier', models.CharField(help_text=b'Identifier used on the command line', max_length=16)),
                ('script', models.TextField(help_text=b'Script to be executed on the nodes. Writeit with atomicity in mind, there is no waranty that the script ends executed multiple times.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='execution',
            name='operation',
            field=models.ForeignKey(related_name='executions', to='maintenance.Operation'),
            preserve_default=True,
        ),
    ]
