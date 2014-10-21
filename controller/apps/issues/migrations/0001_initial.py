# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author_name', models.CharField(max_length=60)),
                ('content', models.TextField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('default', models.BooleanField(default=False)),
                ('notify_group_admins', models.BooleanField(default=True)),
                ('notify_node_admins', models.BooleanField(default=False)),
                ('notify_slice_admins', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_by_name', models.CharField(max_length=60)),
                ('subject', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('visibility', models.CharField(default=b'PUBLIC', max_length=32, choices=[(b'PUBLIC', b'Public'), (b'PRIVATE', b'Private')])),
                ('priority', models.CharField(default=b'MEDIUM', max_length=32, choices=[(b'HIGH', b'High'), (b'MEDIUM', b'Medium'), (b'LOW', b'Low')])),
                ('state', models.CharField(default=b'NEW', max_length=32, choices=[(b'NEW', b'New'), (b'IN_PROGRESS', b'In Progress'), (b'RESOLVED', b'Resolved'), (b'FEEDBACK', b'Feedback'), (b'REJECTED', b'Rejected'), (b'CLOSED', b'Closed')])),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True)),
                ('cc', models.TextField(help_text=b'emails to send a carbon copy', verbose_name=b'CC', blank=True)),
                ('created_by', models.ForeignKey(related_name=b'created_tickets', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('group', models.ForeignKey(related_name=b'assigned_tickets', blank=True, to='users.Group', null=True)),
                ('owner', models.ForeignKey(related_name=b'owned_tickets', verbose_name=b'assigned to', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('queue', models.ForeignKey(related_name=b'tickets', blank=True, to='issues.Queue', null=True)),
            ],
            options={
                'ordering': ['-last_modified_on'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TicketTracker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ticket', models.ForeignKey(to='issues.Ticket')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='tickettracker',
            unique_together=set([('ticket', 'user')]),
        ),
        migrations.AddField(
            model_name='message',
            name='ticket',
            field=models.ForeignKey(related_name=b'messages', to='issues.Ticket'),
            preserve_default=True,
        ),
    ]
