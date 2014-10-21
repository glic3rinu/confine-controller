# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import controller.core.validators
import django.utils.timezone
from django.conf import settings
import django.core.validators
import controller.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('username', controller.models.fields.NullableCharField(null=True, validators=[django.core.validators.RegexValidator(b'^[\\w.+-]+$', b'Enter a valid username.', b'invalid')], max_length=30, blank=True, help_text=b'Optional. A unique user alias for authentication. 30 characters or fewer. Letters, numbers and ./+/-/_ characters.', unique=True, db_index=True)),
                ('email', models.EmailField(help_text=b'Required. A unique email for the user. May be used for authentication.', unique=True, max_length=255, verbose_name=b'Email Address')),
                ('description', models.TextField(help_text=b'An optional free-form textual description of this user, it can include URLs and other information.', blank=True)),
                ('name', controller.models.fields.TrimmedCharField(help_text=b'Required. A unique name for this user. A single non-empty line of free-form text with no whitespace surrounding it.', unique=True, max_length=60, db_index=True, validators=[controller.core.validators.validate_name])),
                ('is_active', models.BooleanField(default=True, help_text=b'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('is_superuser', models.BooleanField(default=False, help_text=b'Designates that this user has all permissions without explicitly assigning them.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.TextField(help_text=b'Authentication token like SSH or other kinds of public keys or X.509 certificates to be used for slivers or experiments. The exact valid format depends on the type of token as long as it is non-empty and only contains ASCII characters (e.g. by using PEM encoding or other ASCII armour).', validators=[controller.core.validators.validate_ascii])),
                ('user', models.ForeignKey(related_name=b'auth_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'authentication token',
                'verbose_name_plural': 'authentication tokens',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'A unique name for this group. A single non-empty line of free-form text with no whitespace surrounding it.', unique=True, max_length=32, validators=[controller.core.validators.validate_name])),
                ('description', models.TextField(blank=True)),
                ('allow_nodes', models.BooleanField(default=False, help_text=b'Whether nodes belonging to this group can be created or set into production (false by default). Its value can only be changed by testbed superusers.')),
                ('allow_slices', models.BooleanField(default=False, help_text=b'Whether slices belonging to this group can be created or instantiated (false by default). Its value can only be changed by testbed superusers.')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JoinRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(related_name=b'join_requests', to='users.Group')),
                ('user', models.ForeignKey(related_name=b'join_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource', models.CharField(max_length=16, choices=[(b'nodes', b'Nodes'), (b'slices', b'Slices')])),
                ('group', models.ForeignKey(related_name=b'resource_requests', to='users.Group')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Roles',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_group_admin', models.BooleanField(default=False, help_text=b'Whether that user is an administrator in this group. An administrator can manage slices and nodes belonging to the group, members in the group and their roles, and the group itself.', verbose_name=b'group admin')),
                ('is_node_admin', models.BooleanField(default=False, help_text=b'Whether that user is a node administrator in this group. A node administrator can manage nodes belonging to the group.', verbose_name=b'node admin (technician)')),
                ('is_slice_admin', models.BooleanField(default=False, help_text=b'Whether that user is a slice administrator in this group. A slice administrator can manage slices belonging to the group.', verbose_name=b'slice admin (researcher)')),
                ('group', models.ForeignKey(related_name=b'roles', to='users.Group')),
                ('user', models.ForeignKey(related_name=b'roles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'roles',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='roles',
            unique_together=set([('user', 'group')]),
        ),
        migrations.AlterUniqueTogether(
            name='joinrequest',
            unique_together=set([('user', 'group')]),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_name=b'users', through='users.Roles', to='users.Group', blank=True),
            preserve_default=True,
        ),
    ]
