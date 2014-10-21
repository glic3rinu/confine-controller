# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import slices.models
import controller.core.validators
import slices.helpers
import controller.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'A unique name of this slice. A single non-empty line of free-form text with no whitespace surrounding it.', unique=True, max_length=64, validators=[controller.core.validators.validate_name])),
                ('description', models.TextField(help_text=b'An optional free-form textual description of this slice.', blank=True)),
                ('expires_on', models.DateField(default=slices.models.get_expires_on, help_text=b'Expiration date of this slice. Automatically deleted once expires.', null=True, blank=True)),
                ('instance_sn', models.PositiveIntegerField(default=0, help_text=b'The number of times this slice has been instructed to be reset (instance sequence number). Automatically incremented by the reset function.', verbose_name=b'instance sequence number', blank=True)),
                ('allow_isolated', models.BooleanField(default=False, help_text=b'Whether to request a VLAN tag for isolated sliver interfaces (see node architecture) at slice deployment time. If the allocation is successful, the tag is stored in the /isolated_vlan_tag member. Otherwise, the deployment of the slice fails', verbose_name=b'Request isolated VLAN tag')),
                ('isolated_vlan_tag', models.IntegerField(help_text=b'VLAN tag allocated to this slice. The only values that can be set are null which means that no VLAN is wanted for the slice, and -1 which asks the server to allocate for the slice a new VLAN tag (100 <= vlan_tag < 0xFFF) while the slice is instantiated (or active). It cannot be changed on an instantiated slice with slivers having isolated interfaces.', null=True, verbose_name=b'Isolated VLAN tag', blank=True)),
                ('set_state', models.CharField(default=b'register', help_text=b'The state set on this slice (set state) and its slivers (if they do not explicitly indicate a lower one). Possible values: register (initial) &lt; deploy &lt; start. See <a href="https://wiki.confine-project.eu/arch:slice-sliver-states">slice and sliver states</a> for the full description of set states and possible transitions.', max_length=16, choices=[(b'register', b'REGISTER'), (b'deploy', b'DEPLOY'), (b'start', b'START')])),
                ('group', models.ForeignKey(related_name=b'slices', to='users.Group')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SliceProp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Per slice unique single line of free-form text with no whitespace surrounding it.', max_length=64, validators=[controller.core.validators.validate_prop_name])),
                ('value', models.CharField(max_length=256)),
                ('slice', models.ForeignKey(related_name=b'properties', to='slices.Slice')),
            ],
            options={
                'verbose_name': 'slice property',
                'verbose_name_plural': 'slice properties',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sliver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(help_text=b'An optional free-form textual description of this sliver.', blank=True)),
                ('instance_sn', models.PositiveIntegerField(default=0, help_text=b'The number of times this sliver has been instructed to be updated (instance sequence number).', verbose_name=b'instance sequence number', blank=True)),
                ('data', models.FileField(help_text=b'File containing data for this sliver.', upload_to=slices.helpers.UploadToGenerator(b'data', b'.', None), verbose_name=b'sliver data', blank=True)),
                ('data_uri', models.CharField(help_text=b'If present, the URI of a file containing data for this sliver, instead of the one specified by the slice. Its format and contents depend on the type of the template to be used.', max_length=256, verbose_name=b'sliver data URI', blank=True)),
                ('data_sha256', models.CharField(blank=True, help_text=b'The SHA256 hash of the sliver data file, used to check its integrity. Compulsory when a file has been specified.', max_length=64, verbose_name=b'sliver data SHA256', validators=[controller.core.validators.validate_sha256])),
                ('overlay', models.FileField(blank=True, help_text=b'File containing overlay for this sliver.', upload_to=slices.helpers.UploadToGenerator(b'overlay', b'.', None), validators=[controller.core.validators.FileExtValidator((b'.tar.gz', b'.tgz'))])),
                ('overlay_uri', models.CharField(help_text=b'If present, the URI of a file containing an overlay for this sliver, instead of the one specified by the slice. The file must be an archive (e.g. a .tar.gz) of the upper directory of an overlayfs filesystem, and will be applied on top of the used template. This member may be set directly or through the do-upload-overlay function.', max_length=256, verbose_name=b'overlay URI', blank=True)),
                ('overlay_sha256', models.CharField(blank=True, help_text=b'The SHA256 hash of the previous file, used to check its integrity. Automatically setted on file upload but compulsory when file URI has been specified.', max_length=64, verbose_name=b'overlay SHA256', validators=[controller.core.validators.validate_sha256])),
                ('set_state', controller.models.fields.NullableCharField(blank=True, max_length=16, null=True, help_text=b'If present, the state set on this sliver (set state), which overrides a higher one specified by the slice (e.g. register overrides start, but start does not override register). Possible values: register (initial) &lt; deploy &lt; start. See <a href="https://wiki.confine-project.eu/arch:slice-sliver-states">slice and sliver states</a> for the full description of set states and possible transitions.', choices=[(b'register', b'REGISTER'), (b'deploy', b'DEPLOY'), (b'start', b'START')])),
                ('node', models.ForeignKey(related_name=b'slivers', to='nodes.Node')),
                ('slice', models.ForeignKey(related_name=b'slivers', to='slices.Slice')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SliverDefaults',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instance_sn', models.PositiveIntegerField(default=0, help_text=b'The instance sequence number that newly created slivers will get. Automatically incremented whenever a sliver of this slice is instructed to be updated.', verbose_name=b'New sliver instance sequence number', blank=True)),
                ('overlay', models.FileField(blank=True, help_text=b'File containing overlay for slivers (if they do not explicitly indicate one)', upload_to=slices.helpers.UploadToGenerator(b'overlay', b'.', None), validators=[controller.core.validators.FileExtValidator((b'.tar.gz', b'.tgz'))])),
                ('overlay_uri', models.CharField(help_text=b'The URI of a file containing an overlay for slivers (if they do not explicitly indicate one). The file must be an archive (e.g. a .tar.gz) of the upper directory of an overlayfs filesystem, and will be applied on top of the used template. This member may be set directly or through the do-upload-overlay function.', max_length=256, verbose_name=b'overlay URI', blank=True)),
                ('overlay_sha256', models.CharField(blank=True, help_text=b'The SHA256 hash of the previous file, used to check its integrity. This member may be set directly or through the do-upload-overlay function. Compulsory when a file has been specified.', max_length=64, verbose_name=b'overlay SHA256', validators=[controller.core.validators.validate_sha256])),
                ('data', models.FileField(help_text=b'File containing experiment data for slivers (if they do not explicitly indicate one)', upload_to=slices.helpers.UploadToGenerator(b'data', b'.', None), verbose_name=b'sliver data', blank=True)),
                ('data_uri', models.CharField(help_text=b'The URI of a file containing sliver data for slivers (if they do not explicitly indicate one). Its format and contents depend on the type of the template to be used.', max_length=256, verbose_name=b'sliver data URI', blank=True)),
                ('data_sha256', models.CharField(blank=True, help_text=b'The SHA256 hash of the data file, used to check its integrity. Compulsory when a file has been specified.', max_length=64, verbose_name=b'sliver data SHA256', validators=[controller.core.validators.validate_sha256])),
                ('set_state', models.CharField(default=b'start', help_text=b'The state set by default on its slivers (set state). Possible values: register &lt; deploy &lt; start (default). See <a href="https://wiki.confine-project.eu/arch:slice-sliver-states">slice and sliver states</a> for the full description of set states and possible transitions.', max_length=16, choices=[(b'register', b'REGISTER'), (b'deploy', b'DEPLOY'), (b'start', b'START')])),
                ('slice', models.OneToOneField(related_name=b'sliver_defaults', to='slices.Slice')),
            ],
            options={
                'verbose_name_plural': 'sliver defaults',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SliverIface',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nr', models.PositiveIntegerField(help_text=b'The unique 8-bit, positive integer number of this interface in this sliver. Interface #0 is always the private interface.', verbose_name=b'number')),
                ('name', models.CharField(help_text=b'The name of this interface. It must match the regular expression ^[a-z]+[0-9]*$ and have no more than 10 characters.', max_length=10, validators=[controller.core.validators.validate_net_iface_name])),
                ('type', models.CharField(help_text=b"The type of this interface. Types public4 and public6 are only available if the node's sliver_pub_ipv4 and sliver_pub_ipv6 respectively are not none. There can only be one interface of type private, and by default it is configured for both IP4 and IPv6 default routes using the RD's internal addresses. The first public4 interface declared is configured for the default IPv4 route using the CD's IPv4 gateway address, and similarly with public6 interfaces for IPv6.", max_length=16, choices=[(b'public6', b'Public6'), (b'public4', b'Public4'), (b'management', b'Management'), (b'isolated', b'Isolated'), (b'private', b'Private'), (b'debug', b'Debug')])),
                ('parent', models.ForeignKey(blank=True, to='nodes.DirectIface', help_text=b"The name of a direct interface in the research device to use for this interface's traffic (VLAN-tagged); the slice must have a non-null isolated_vlan_tag. Only meaningful (and mandatory) for isolated interfaces.", null=True)),
                ('sliver', models.ForeignKey(related_name=b'interfaces', to='slices.Sliver')),
            ],
            options={
                'verbose_name': 'sliver interface',
                'verbose_name_plural': 'sliver interfaces',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SliverProp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Per slice unique single line of free-form text with no whitespace surrounding it', max_length=64, validators=[controller.core.validators.validate_prop_name])),
                ('value', models.CharField(max_length=256)),
                ('sliver', models.ForeignKey(related_name=b'properties', to='slices.Sliver')),
            ],
            options={
                'verbose_name': 'sliver property',
                'verbose_name_plural': 'sliver properties',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The unique name of this template. A single line of free-form text with no whitespace surrounding it, it can include version numbers and other information.', unique=True, max_length=32, validators=[controller.core.validators.validate_name])),
                ('description', models.TextField(help_text=b'An optional free-form textual description of this template.', blank=True)),
                ('type', models.CharField(default=b'', help_text=b'The system type of this template. Roughly equivalent to the distribution the template is based on, e.g. debian (Debian, Ubuntu...), fedora (Fedora, RHEL...), suse (openSUSE, SUSE Linux Enterprise...). To instantiate a sliver based on a template, the research device must support its type.', max_length=32, choices=[(b'debian', b'Debian'), (b'openwrt', b'OpenWRT')])),
                ('node_archs', controller.models.fields.MultiSelectField(default=b'i686', help_text=b'The node architectures accepted by this template (as reported by uname -m, non-empty). Slivers using this template should run on nodes whose architecture is listed here.', max_length=256, choices=[(b'x86_64', b'x86_64'), (b'i586', b'i586'), (b'i686', b'i686')])),
                ('is_active', models.BooleanField(default=True)),
                ('image', models.FileField(help_text=b"Template's image file.", upload_to=slices.helpers.UploadToGenerator(b'image', b'.', None), validators=[controller.core.validators.FileExtValidator((b'.tar.gz', b'.tgz'))])),
                ('image_uri', models.CharField(help_text=b'The URI of a file containing an image for slivers (if they do not explicitly indicate one). The file must be an archive (e.g. a .tar.gz) of the upper directory of an overlayfs filesystem, and will be applied on top of the used template. This member may be set directly or through the do-upload-overlay function.', max_length=256, verbose_name=b'image URI', blank=True)),
                ('image_sha256', models.CharField(blank=True, help_text=b'The SHA256 hash of the image file, used to check its integrity. Compulsory when a file has been specified.', max_length=64, verbose_name=b'image SHA256', validators=[controller.core.validators.validate_sha256])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='sliverprop',
            unique_together=set([('sliver', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='sliveriface',
            unique_together=set([('sliver', 'name')]),
        ),
        migrations.AddField(
            model_name='sliverdefaults',
            name='template',
            field=models.ForeignKey(help_text=b'The template to be used by the slivers of this slice (if they do not explicitly indicate one).', to='slices.Template'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sliver',
            name='template',
            field=models.ForeignKey(blank=True, to='slices.Template', help_text=b'If present, the template to be used by this sliver, instead of the one specified by the slice.', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='sliver',
            unique_together=set([('slice', 'node')]),
        ),
        migrations.AlterUniqueTogether(
            name='sliceprop',
            unique_together=set([('slice', 'name')]),
        ),
    ]
