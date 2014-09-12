# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


def get_config(orm):
    """Get or create the firmware Config object."""
    if not orm.Config.objects.exists():
        # Initialize firmware data
        create_initial_objects(orm)
    return orm.Config.objects.get()

def create_initial_objects(orm):
    """
    Use South ORM to create objects instead of using fixtures!
    firmware/fixtures/firmwareconfig.json is not longer necessary
    """
    config = orm.Config.objects.create(**{
        "version": "0.1",
        "description": "Confine Firmware",
        "image_name": "confine-firmware-%(node_name)s-%(arch)s.img.gz"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "node node",
        "config": config,
        "option": "id",
        "value": "'%.4x' % node.id"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "node node",
        "config": config,
        "option": "local_ifname",
        "value": "node.local_iface"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "node node",
        "config": config,
        "option": "mac_prefix16",
        "value": "':'.join(re.findall('..', node.get_sliver_mac_prefix()[2:6]))"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "node node",
        "config": config,
        "option": "priv_ipv4_prefix24",
        "value": "node.get_priv_ipv4_prefix().split('.0/24')[0]"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "node node",
        "config": config,
        "option": "public_ipv4_avail",
        "value": "str(node.sliver_pub_ipv4_num)"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "node node",
        "config": config,
        "option": "rd_public_ipv4_proto",
        "value": "'dhcp'"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "node node",
        "config": config,
        "option": "sl_public_ipv4_proto",
        "value": "'dhcp'"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "node node",
        "config": config,
        "option": "rd_if_iso_parents",
        "value": "' '.join(node.direct_ifaces.values_list('name', flat=True))"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "testbed testbed",
        "config": config,
        "option": "mgmt_ipv6_prefix48",
        "value": "MGMT_IPV6_PREFIX.split('::')[0]"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "tinc-net confine",
        "config": config,
        "option": "enabled",
        "value": "'1'"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "node node",
        "config": config,
        "option": "state",
        "value": "'prepared'"
    })
    orm.ConfigUCI.objects.create(**{
        "section": "server server",
        "config": config,
        "option": "base_path",
        "value": "'/api'"
    })
    orm.ConfigFile.objects.create(**{
        "priority": 0,
        "is_active": True,
        "content": "self.config.render_uci(node, sections=['node node', 'server server', 'testbed testbed'])",
        "mode": "",
        "is_optional": False,
        "path": "/etc/config/confine",
        "config": config
    })
    orm.ConfigFile.objects.create(**{
        "priority": 0,
        "is_active": True,
        "content": "[ server.get_host(island=node.island) for server in node.tinc.connect_to ]",
        "mode": "",
        "is_optional": False,
        "path": "[ \"/etc/tinc/confine/hosts/%s\" % server for server in node.tinc.connect_to ]",
        "config": config
    })
    file_3 = orm.ConfigFile.objects.create(**{
        "priority": 1,
        "is_active": True,
        "content": "node.tinc.generate_key(commit=True)",
        "mode": "og-rw",
        "is_optional": True,
        "path": "/etc/tinc/confine/rsa_key.priv",
        "config": config
    })
    orm.ConfigFile.objects.create(**{
        "priority": 0,
        "is_active": True,
        "content": "node.tinc.get_host()",
        "mode": "",
        "is_optional": False,
        "path": "'/etc/tinc/confine/hosts/%s' % node.tinc.name",
        "config": config
    })
    orm.ConfigFile.objects.create(**{
        "priority": 0,
        "is_active": True,
        "content": "node.tinc.get_config()",
        "mode": "",
        "is_optional": False,
        "path": "/etc/tinc/confine/tinc.conf",
        "config": config
    })
    orm.ConfigFile.objects.create(**{
        "priority": 0,
        "is_active": False,
        "content": "node.tinc.get_tinc_up()",
        "mode": "+x",
        "is_optional": False,
        "path": "/etc/tinc/confine/tinc-up",
        "config": config
    })
    orm.ConfigFile.objects.create(**{
        "priority": 0,
        "is_active": False,
        "content": "node.tinc.get_tinc_down()",
        "mode": "+x",
        "is_optional": False,
        "path": "/etc/tinc/confine/tinc-down",
        "config": config
    })
    orm.ConfigFile.objects.create(**{
        "priority": 0,
        "is_active": False,
        "content": "self.config.render_uci(node, sections=['tinc-net confine'])",
        "mode": "",
        "is_optional": False,
        "path": "/etc/config/tinc",
        "config": config
    })
    file_9 = orm.ConfigFile.objects.create(**{
        "priority": 0,
        "is_active": True,
        "content": "node.generate_certificate(key=files[0].content, commit=True).strip()",
        "mode": "",
        "is_optional": True,
        "path": "/etc/uhttpd.crt.pem",
        "config": config
    })
    file_10 = orm.ConfigFile.objects.create(**{
        "priority": 0,
        "is_active": True,
        "content": "files[0].content",
        "mode": "og-rw",
        "is_optional": True,
        "path": "/etc/uhttpd.key.pem",
        "config": config
    })
    orm.ConfigFileHelpText.objects.create(**{
        "help_text": "This file is the private key for the management overlay. \r\nNotice that the node public key will be automatically updated and your node may lose connectivity to the management network until the new image is installed.\r\n",
        "config": config,
        "file": file_3
    })
    orm.ConfigFileHelpText.objects.create(**{
        "help_text": "This file contains the certificate for node authentication.\r\nPlease notice that this depends on the RSA keys generated for the tinc overlay, so you must also select the rsa_key.priv if you want a certificate. Also if there is any node.certificate it will be overwritten.",
        "config": config,
        "file": file_9
    })
    orm.ConfigFileHelpText.objects.create(**{
        "help_text": "This file contains the node private key for uhttpd service.\r\nYou should also select /etc/tinc/confine/rsa_key.priv for generating this file.\r\n",
        "config": config,
        "file": file_10
    })


class Migration(DataMigration):

    def forwards(self, orm):
        "Create ConfigUCI for node's authorized_keys #188."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        config = get_config(orm)
        orm.ConfigUCI.objects.create(config=config, section='node node',
            option='sync_node_admins', value="'1' if node.keys.sync_node_admins else '0'")

    def backwards(self, orm):
        "Remove created ConfigUCI."
        config = get_config(orm)
        orm.ConfigUCI.objects.get(section='node node', option='sync_node_admins', config=config).delete()

    models = {
        u'firmware.baseimage': {
            'Meta': {'object_name': 'BaseImage'},
            'architectures': ('controller.models.fields.MultiSelectField', [], {'max_length': '250'}),
            'config': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': u"orm['firmware.Config']"}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        },
        u'firmware.build': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Build'},
            'base_image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'image': ('privatefiles.models.fields.PrivateFileField', [], {'max_length': '256'}),
            'kwargs': ('django.db.models.fields.TextField', [], {}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'firmware_build'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['nodes.Node']"}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'firmware.buildfile': {
            'Meta': {'unique_together': "(('build', 'path'),)", 'object_name': 'BuildFile'},
            'build': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': u"orm['firmware.Build']"}),
            'config': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': u"orm['firmware.ConfigFile']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'firmware.config': {
            'Meta': {'object_name': 'Config'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_name': ('django.db.models.fields.CharField', [], {'default': "'firmware-%(node_name)s-%(arch)s-%(version)s-%(build_id)d.img.gz'", 'max_length': '255'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'firmware.configfile': {
            'Meta': {'ordering': "['-priority']", 'unique_together': "(['config', 'path'],)", 'object_name': 'ConfigFile'},
            'config': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': u"orm['firmware.Config']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_optional': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'firmware.configfilehelptext': {
            'Meta': {'object_name': 'ConfigFileHelpText'},
            'config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['firmware.Config']"}),
            'file': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'help_text'", 'unique': 'True', 'to': u"orm['firmware.ConfigFile']"}),
            'help_text': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'firmware.configplugin': {
            'Meta': {'object_name': 'ConfigPlugin'},
            'config': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'plugins'", 'to': u"orm['firmware.Config']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'blank': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        u'firmware.configuci': {
            'Meta': {'ordering': "['section', 'option']", 'unique_together': "(['config', 'section', 'option'],)", 'object_name': 'ConfigUCI'},
            'config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['firmware.Config']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'section': ('django.db.models.fields.CharField', [], {'default': "'node'", 'max_length': '32'}),
            'value': ('django.db.models.fields.TextField', [], {'max_length': '255'})
        },
        u'firmware.nodebuildfile': {
            'Meta': {'unique_together': "(('node', 'path'),)", 'object_name': 'NodeBuildFile'},
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': u"orm['nodes.Node']"}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'firmware.nodekeys': {
            'Meta': {'object_name': 'NodeKeys'},
            'allow_node_admins': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'keys'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['nodes.Node']"}),
            'ssh_auth': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ssh_pass': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'sync_node_admins': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'nodes.island': {
            'Meta': {'object_name': 'Island'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'arch': ('django.db.models.fields.CharField', [], {'default': "'i686'", 'max_length': '16'}),
            'boot_sn': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'cert': ('controller.models.fields.NullableTextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodes.Island']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'local_iface': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'priv_ipv4_prefix': ('controller.models.fields.NullableCharField', [], {'max_length': '19', 'null': 'True', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'debug'", 'max_length': '16'}),
            'sliver_mac_prefix': ('controller.models.fields.NullableCharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv4': ('django.db.models.fields.CharField', [], {'default': "'dhcp'", 'max_length': '8'}),
            'sliver_pub_ipv4_range': ('controller.models.fields.NullableCharField', [], {'default': "'#8'", 'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv6': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '8'})
        },
        u'users.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
            'allow_nodes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_slices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        }
    }

    complete_apps = ['firmware']
    symmetrical = True
