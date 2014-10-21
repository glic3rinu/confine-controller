# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import controller.core.validators
import nodes.validators
import controller.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectIface',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The name of the interface used as a local interface (non-empty). See <a href="https://wiki.confine-project.eu/arch:node">node architecture</a>.', max_length=16, validators=[controller.core.validators.validate_net_iface_name])),
            ],
            options={
                'verbose_name': 'direct network interface',
                'verbose_name_plural': 'direct network interfaces',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Island',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The unique name of this island. A single line of free-form text with no whitespace surrounding it.', unique=True, max_length=32, validators=[controller.core.validators.validate_name])),
                ('description', models.TextField(help_text=b'Optional free-form textual description of this island.', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'A unique name for this node. A single non-empty line of free-form text with no whitespace surrounding it.', unique=True, max_length=256, validators=[controller.core.validators.validate_name])),
                ('description', models.TextField(help_text=b'Free-form textual description of this host/device.', blank=True)),
                ('arch', models.CharField(default=b'i686', help_text=b'Architecture of this RD (as reported by uname -m).', max_length=16, verbose_name=b'Architecture', choices=[(b'x86_64', b'x86_64'), (b'i586', b'i586'), (b'i686', b'i686')])),
                ('local_iface', models.CharField(default=b'eth0', help_text=b'Name of the interface used as a local interface. See <a href="wiki.confine-project.eu/arch:node">node architecture</a>.', max_length=16, verbose_name=b'Local interface', validators=[controller.core.validators.validate_net_iface_name])),
                ('sliver_pub_ipv6', models.CharField(default=b'none', help_text=b'Indicates IPv6 support for public sliver interfaces in the local network (see <a href="https://wiki.confine-project.eu/arch:node">node architecture</a>). Possible values: none (no public IPv6 support), dhcp (addresses configured using DHCPv6), auto (addresses configured using NDP stateless autoconfiguration).', max_length=8, verbose_name=b'Sliver public IPv6', choices=[(b'none', b'None'), (b'dhcp', b'DHCP'), (b'auto', b'Auto')])),
                ('sliver_pub_ipv4', models.CharField(default=b'dhcp', help_text=b'Indicates IPv4 support for public sliver interfaces in the local network (see <a href="https://wiki.confine-project.eu/arch:node">node architecture</a>). Possible values: none (no public IPv4 support), dhcp (addresses configured using DHCP), range (addresses chosen from a range, see <em>Sliver public IPv4 range</em>).', max_length=8, verbose_name=b'Sliver public IPv4', choices=[(b'none', b'None'), (b'dhcp', b'DHCP'), (b'range', b'Range')])),
                ('sliver_pub_ipv4_range', controller.models.fields.NullableCharField(default=b'#8', max_length=256, blank=True, help_text=b"Describes the public IPv4 range that can be used by sliver public interfaces. If <em>Sliver public IPv4</em> is <em>none</em>, its value is null. If <em>Sliver public IPv4</em> is <em>dhcp</em>, its value is <em>#N</em>, where N is the decimal integer number of DHCP addresses reserved for slivers. If <em>Sliver public IPv4</em> is <em>range</em>, its value is <em>BASE_IP#N</em>, where N is the decimal integer number of consecutive addresses reserved for slivers after and including the range's base address BASE_IP (an IP address in the local network).", null=True, verbose_name=b'Sliver public IPv4 range')),
                ('sliver_mac_prefix', controller.models.fields.NullableCharField(validators=[nodes.validators.validate_sliver_mac_prefix], max_length=5, blank=True, help_text=b'A 16-bit integer number in 0x-prefixed hexadecimal notation used as the node sliver MAC prefix. See <a href="http://wiki.confine-project.eu/arch:addressing">addressing</a> for legal values. 0x54c0 when null.', null=True, verbose_name=b'Sliver MAC prefix')),
                ('priv_ipv4_prefix', controller.models.fields.NullableCharField(validators=[nodes.validators.validate_priv_ipv4_prefix], max_length=19, blank=True, help_text=b'IPv4 /24 network in CIDR notation used as a node private IPv4 prefix. See <a href="http://wiki.confine-project.eu/arch:addressing">addressing</a> for legal values. 192.168.241.0/24 When null.', null=True, verbose_name=b'Private IPv4 prefix')),
                ('boot_sn', models.IntegerField(default=0, help_text=b'Number of times this RD has been instructed to be rebooted.', verbose_name=b'Boot sequence number', blank=True)),
                ('set_state', models.CharField(default=b'debug', help_text=b'The state set on this node (set state). Possible values: debug (initial), safe, production, failure. To support the late addition or generation of node keys, the set state is forced to remain debug while the node is missing some key, certificate or other configuration item. The set state is automatically changed to safe when all items are in place. Changing existing keys also moves the node into state debug or safe as appropriate. All set states but debug can be manually selected. See <a href="https://wiki.confine-project.eu/arch:node-states">node states</a> for the full description of set states and possible transitions.', max_length=16, choices=[(b'debug', b'DEBUG'), (b'safe', b'SAFE'), (b'production', b'PRODUCTION'), (b'failure', b'FAILURE')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NodeApi',
            fields=[
                ('base_uri', models.URLField(help_text=b'The base URI of the API endpoint.', max_length=256, verbose_name=b'base URI')),
                ('cert', controller.models.fields.PEMCertificateField(help_text=b"An optional X.509 PEM-encoded certificate for the API endpoint. Providing this may save API clients from checking the API certificate's signature.", unique=True, null=True, verbose_name=b'Certificate', blank=True)),
                ('type', models.CharField(default=b'node', max_length=16, choices=[(b'node', b'Node')])),
                ('node', models.OneToOneField(related_name=b'_api', primary_key=True, serialize=False, to='nodes.Node')),
            ],
            options={
                'verbose_name': 'node API',
                'verbose_name_plural': 'node API',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NodeProp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Per node unique single line of free-form text with no whitespace surrounding it.', max_length=32, validators=[controller.core.validators.validate_prop_name])),
                ('value', models.CharField(max_length=256)),
                ('node', models.ForeignKey(related_name=b'properties', to='nodes.Node')),
            ],
            options={
                'verbose_name': 'node property',
                'verbose_name_plural': 'node properties',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'A unique name for this server. A single non-empty line of free-form text with no whitespace surrounding it.', unique=True, max_length=256, validators=[controller.core.validators.validate_name])),
                ('description', models.TextField(help_text=b'Free-form textual description of this server.', blank=True)),
            ],
            options={
                'ordering': ['pk'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServerApi',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('base_uri', models.URLField(help_text=b'The base URI of the API endpoint.', max_length=256, verbose_name=b'base URI')),
                ('cert', controller.models.fields.PEMCertificateField(help_text=b"An optional X.509 PEM-encoded certificate for the API endpoint. Providing this may save API clients from checking the API certificate's signature.", unique=True, null=True, verbose_name=b'Certificate', blank=True)),
                ('type', models.CharField(max_length=16, choices=[(b'registry', b'Registry'), (b'controller', b'Controller')])),
                ('island', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='nodes.Island', help_text=b'An optional island used to hint where this API endpoint is reachable from. An API endpoint reachable from the management network may omit this member.', null=True)),
                ('server', models.ForeignKey(related_name=b'api', to='nodes.Server')),
            ],
            options={
                'verbose_name': 'server API',
                'verbose_name_plural': 'server APIs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServerProp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Per node unique single line of free-form text with no whitespace surrounding it.', max_length=32, validators=[controller.core.validators.validate_prop_name])),
                ('value', models.CharField(max_length=256)),
                ('server', models.ForeignKey(related_name=b'properties', to='nodes.Server')),
            ],
            options={
                'verbose_name': 'server property',
                'verbose_name_plural': 'server properties',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='serverprop',
            unique_together=set([('server', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='nodeprop',
            unique_together=set([('node', 'name')]),
        ),
        migrations.AddField(
            model_name='node',
            name='group',
            field=models.ForeignKey(related_name=b'nodes', to='users.Group', help_text=b'The group this node belongs to. The user creating this node must be a group or node administrator of this group, and the group must have node creation allowed (/allow_nodes=true). Node and group administrators in this group are able to manage this node.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='island',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='nodes.Island', help_text=b'An optional island used to hint where the node is located network-wise.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='directiface',
            name='node',
            field=models.ForeignKey(related_name=b'direct_ifaces', to='nodes.Node'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='directiface',
            unique_together=set([('name', 'node')]),
        ),
    ]
