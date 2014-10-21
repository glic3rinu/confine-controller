# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import controller.core.validators
import django.core.files.storage
import privatefiles.models.fields
import controller.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Unique name for this base image.A single non-empty line of free-form text with no whitespace surrounding it. ', unique=True, max_length=256, validators=[controller.core.validators.validate_name])),
                ('architectures', controller.models.fields.MultiSelectField(max_length=250, choices=[(b'x86_64', b'x86_64'), (b'i586', b'i586'), (b'i686', b'i686')])),
                ('image', models.FileField(help_text=b'Image file compressed in gzip. The file name must end in .img.gz', upload_to=b'.', validators=[controller.core.validators.FileExtValidator((b'.img.gz',))])),
                ('default', models.BooleanField(default=False, help_text=b'If true this base image will be preselected on the firmware generation form')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Build',
            fields=[
                ('node', models.OneToOneField(related_name=b'firmware_build', primary_key=True, serialize=False, to='nodes.Node')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('version', models.CharField(max_length=64)),
                ('image', privatefiles.models.fields.PrivateFileField(storage=django.core.files.storage.FileSystemStorage(location=b'/var/lib/vct/images'), max_length=256, upload_to=b'.')),
                ('base_image', models.FileField(help_text=b'Image file compressed in gzip. The file name must end in .img.gz', upload_to=b'.')),
                ('task_id', models.CharField(help_text=b'Celery task ID', max_length=36, unique=True, null=True)),
                ('kwargs', models.TextField()),
            ],
            options={
                'ordering': ['-date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BuildFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=256)),
                ('content', models.TextField()),
                ('build', models.ForeignKey(related_name=b'files', to='firmware.Build')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=64)),
                ('image_name', models.CharField(default=b'firmware-%(node_name)s-%(arch)s-%(version)s-%(build_id)d.img.gz', help_text=b'Image file name. Available variables: %(node_name)s, %(arch)s, %(build_id)d, %(version)s and %(node_id)d', max_length=255)),
            ],
            options={
                'verbose_name': 'Firmware config',
                'verbose_name_plural': 'Firmware config',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConfigFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=256)),
                ('content', models.TextField()),
                ('mode', models.CharField(max_length=6, blank=True)),
                ('priority', models.IntegerField(default=0)),
                ('is_optional', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('config', models.ForeignKey(related_name=b'files', to='firmware.Config')),
            ],
            options={
                'ordering': ['-priority'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConfigFileHelpText',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('help_text', models.TextField()),
                ('config', models.ForeignKey(to='firmware.Config')),
                ('file', models.OneToOneField(related_name=b'help_text', to='firmware.ConfigFile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConfigPlugin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=False)),
                ('label', models.CharField(unique=True, max_length=128, blank=True)),
                ('module', models.CharField(max_length=256, blank=True)),
                ('config', models.ForeignKey(related_name=b'plugins', to='firmware.Config')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConfigUCI',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('section', models.CharField(default=b'node', help_text=b'UCI config statement', max_length=32)),
                ('option', models.CharField(help_text=b'UCI option statement', max_length=32)),
                ('value', models.TextField(help_text=b"Python code that will be evaluated for obtining the value from the node. I.e. node.properties['ip']", max_length=255)),
                ('config', models.ForeignKey(to='firmware.Config')),
            ],
            options={
                'ordering': ['section', 'option'],
                'verbose_name_plural': 'Config UCI',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NodeBuildFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=256)),
                ('content', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NodeKeys',
            fields=[
                ('allow_node_admins', models.BooleanField(default=True, help_text=b"Enable this option to permanently allow the current group and node administrators' SSH keys to log into the node as root.", verbose_name=b'Allow current node admins')),
                ('sync_node_admins', models.BooleanField(default=False, help_text=b"Enable this option to also allow current or future group and node administrators' SSH keys (as configured in the registry) to log into the node as root. Please note that this may expose your node to an attack if the testbed registry is compromised.", verbose_name=b'Synchronize node admins')),
                ('ssh_auth', models.TextField(help_text=b'Enter additional SSH keys (in "authorized_keys" format) permanently allowed to log into the node as root. You may leave the default keys to allow centralized maintenance of your node by the controller. Please note that this may expose your node to an attack if the controller is compromised.', null=True, verbose_name=b'Additional keys', blank=True)),
                ('ssh_pass', models.CharField(max_length=128, null=True, blank=True)),
                ('node', models.OneToOneField(related_name=b'keys', primary_key=True, serialize=False, to='nodes.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='nodebuildfile',
            name='node',
            field=models.ForeignKey(related_name=b'files', to='nodes.Node'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='nodebuildfile',
            unique_together=set([('node', 'path')]),
        ),
        migrations.AlterUniqueTogether(
            name='configuci',
            unique_together=set([('config', 'section', 'option')]),
        ),
        migrations.AlterUniqueTogether(
            name='configfile',
            unique_together=set([('config', 'path')]),
        ),
        migrations.AddField(
            model_name='buildfile',
            name='config',
            field=models.ForeignKey(related_name=b'files', to='firmware.ConfigFile'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='buildfile',
            unique_together=set([('build', 'path')]),
        ),
        migrations.AddField(
            model_name='baseimage',
            name='config',
            field=models.ForeignKey(related_name=b'images', to='firmware.Config'),
            preserve_default=True,
        ),
    ]
