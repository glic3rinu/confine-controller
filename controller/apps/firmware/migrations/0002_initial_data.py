# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def init_firmware_config(apps, schema_editor):
    ### Config ###
    Config = apps.get_model("firmware", "Config")
    config = Config.objects.create(version="0.1", description="Confine Firmware",
        image_name="confine-firmware-%(node_name)s-%(arch)s.img.gz")
    
    ### ConfigUCI ###
    ConfigUCI = apps.get_model("firmware", "ConfigUCI")
    ConfigUCI.objects.bulk_create([
        ConfigUCI(
            config=config,
            section="node node",
            option="id",
            value="'%.4x' % node.id"
		),
        ConfigUCI(
            config=config,
            section="node node",
            option="local_ifname",
            value="node.local_iface"
		),
        ConfigUCI(
            config=config,
            section="node node",
            option="mac_prefix16",
            value="':'.join(re.findall('..', node.get_sliver_mac_prefix()[2:6]))"
		),
        ConfigUCI(
            config=config,
            section="node node",
            option="priv_ipv4_prefix24",
            value="node.get_priv_ipv4_prefix().split('.0/24')[0]"
		),
        ConfigUCI(
            config=config,
            section="node node",
            option="public_ipv4_avail",
            value="str(node.sliver_pub_ipv4_num)"
		),
        ConfigUCI(
            config=config,
            section="node node",
            option="rd_public_ipv4_proto",
            value="'dhcp'"
		),
        ConfigUCI(
            config=config,
            section="node node",
            option="sl_public_ipv4_proto",
            value="'dhcp'"
		),
        ConfigUCI(
            config=config,
            section="node node",
            option="rd_if_iso_parents",
            value="' '.join(node.direct_ifaces.values_list('name', flat=True))"
		),
        ConfigUCI(
            config=config,
            section="testbed testbed",
            option="mgmt_ipv6_prefix48",
            value="MGMT_IPV6_PREFIX.split('::')[0]"
		),
        ConfigUCI(
            config=config,
            section="tinc-net confine",
            option="enabled",
            value="'1'"
		),
        ConfigUCI(
            config=config,
            section="node node",
            option="state",
            value="'prepared'"
		),
        ConfigUCI(
            config=config,
            section="server server",
            option="base_path",
            value="'/api'"
		),
        
        # South 0034_datamigration__add__configuc_sync_node_admins.py
        # Create ConfigUCI for node's authorized_keys #188.
        ConfigUCI(
            config=config,
            section='node node',
            option='sync_node_admins',
            value="'1' if node.keys.sync_node_admins else '0'"
		),
        
        # South 0035_datamigration__add_registry_uci.py
        # Update firmware configuration to include registry section.
        ConfigUCI(
            config=config,
            section='registry registry',
            option='base_uri',
            value="node.firmware_build.kwargs_dict.get('registry_base_uri')"
		),
        ConfigUCI(
            config=config,
            section='registry registry',
            option='cert',
            value="'/etc/confine/registry-server.crt'"
		),
    ])
    
    ### ConfigFile ###
    # TODO (eventually): break backwards compatibility with old node firmware #245 note-25
    # ConfigUCI.objects.filter(section='server server', option='base_path').delete()
    ### Update Config file /etc/config/confine ###
    # TODO (eventually): break backwards compatibility: remove 'server server' section
    # on ConfigFile /etc/config/confine
    
    ConfigFile = apps.get_model("firmware", "ConfigFile")
    ConfigFile.objects.bulk_create([
        ConfigFile(
            priority=0,
            is_active= True,
            # includes South 0035_datamigration__add_registry_uci.py update
            content="self.config.render_uci(node, sections=['node node', 'server server', 'testbed testbed', 'registry registry'])",
            mode="",
            is_optional=False,
            path="/etc/config/confine",
            config=config
        ),
        ConfigFile(
            priority=0,
            is_active= True,
            content="[ server.get_host(island=node.island) for server in node.tinc.connect_to ]",
            mode="",
            is_optional=False,
            path="[ \"/etc/tinc/confine/hosts/%s\" % server for server in node.tinc.connect_to ]",
            config=config
        ),
        ConfigFile(
            priority=1,
            is_active= True,
            content="node.tinc.generate_key(commit=True)",
            mode="og-rw",
            is_optional=True,
            path="/etc/tinc/confine/rsa_key.priv",
            config=config
        ),
        ConfigFile(
            priority=0,
            is_active= True,
            content="node.tinc.get_host()",
            mode="",
            is_optional=False,
            path="'/etc/tinc/confine/hosts/%s' % node.tinc.name",
            config=config
        ),
        ConfigFile(
            priority=0,
            is_active= True,
            content="node.tinc.get_config()",
            mode="",
            is_optional=False,
            path="/etc/tinc/confine/tinc.conf",
            config=config
        ),
        ConfigFile(
            priority=0,
            is_active= False,
            content="node.tinc.get_tinc_up()",
            mode="+x",
            is_optional=False,
            path="/etc/tinc/confine/tinc-up",
            config=config
        ),
        ConfigFile(
            priority=0,
            is_active= False,
            content="node.tinc.get_tinc_down()",
            mode="+x",
            is_optional=False,
            path="/etc/tinc/confine/tinc-down",
            config=config
        ),
        ConfigFile(
            priority=0,
            is_active= False,
            content="self.config.render_uci(node, sections=['tinc-net confine'])",
            mode="",
            is_optional=False,
            path="/etc/config/tinc",
            config=config
        ),
        ConfigFile(
            priority=0,
            is_active= True,
            content="node.generate_certificate(key=files[0].content, commit=True).strip()",
            mode="",
            is_optional=True,
            path="/etc/uhttpd.crt.pem",
            config=config
        ),
        ConfigFile(
            priority=0,
            is_active= True,
            content="files[0].content",
            mode="og-rw",
            is_optional=True,
            path="/etc/uhttpd.key.pem",
            config=config
        ),
    ])
    
    ### ConfigFileHelp ###
    ConfigFileHelpText = apps.get_model("firmware", "ConfigFileHelpText")
    ConfigFileHelpText.objects.bulk_create([
        ConfigFileHelpText(
            config=config,
            file=ConfigFile.objects.get(path="/etc/tinc/confine/rsa_key.priv"),
            help_text=("This file is the private key for the management overlay.\n"
                       "Notice that the node public key will be automatically "
                       "updated and your node may lose connectivity to the "
                       "management network until the new image is installed.\n"),
        ),
        ConfigFileHelpText(
            config=config,
            file=ConfigFile.objects.get(path="/etc/uhttpd.crt.pem"),
            help_text=("This file contains the certificate for node authentication.\n"
                       "Please notice that this depends on the RSA keys generated "
                       "for the tinc overlay, so you must also select the rsa_key.priv "
                       "if you want a certificate. Also if there is any node.certificate "
                       "it will be overwritten."),
        ),
        ConfigFileHelpText(
            config=config,
            file=ConfigFile.objects.get(path="/etc/uhttpd.key.pem"),
            help_text=("This file contains the node private key for uhttpd service.\n"
                       "You should also select /etc/tinc/confine/rsa_key.priv for "
                       "generating this file.\n"),
        )
    ])


def drop_firmware_config(apps, schema_editor):
    Config = apps.get_model("firmware", "Config")
    Config.objects.all().delete()
    
    ConfigUCI = apps.get_model("firmware", "ConfigUCI")
    ConfigUCI.objects.all().delete()
    
    ConfigFile = apps.get_model("firmware", "ConfigFile")
    ConfigFile.objects.all().delete()
    
    ConfigFileHelpText = apps.get_model("firmware", "ConfigFileHelpText")
    ConfigFileHelpText.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('firmware', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_firmware_config, drop_firmware_config),
    ]
