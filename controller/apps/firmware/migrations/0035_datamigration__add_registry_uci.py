# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        "Update firmware configuration to include registry section."
        ### Update ConfigUCI ###
        config = orm.Config.objects.get()
        orm.ConfigUCI.objects.create(section='registry registry', option='base_uri',
            value="node.firmware_build.kwargs_dict.get('registry_base_uri')", config=config)
        orm.ConfigUCI.objects.create(section='registry registry', option='cert',
            value="'/etc/confine/registry-server.crt'", config=config)
        # TODO (eventually): break backwards compatibility with old node firmware #245 note-25
        # orm.ConfigUCI.objects.filter(section='server server', option='base_path').delete()

        ### Update Config file /etc/config/confine ###
        # TODO (eventually): break backwards compatibility: remove 'server server' section
        cfile = orm.ConfigFile.objects.get(path='/etc/config/confine')
        new_content = cfile.content.replace("])", ", 'registry registry'])")
        assert 'registry registry' in new_content
        cfile.content = new_content
        cfile.save()

    def backwards(self, orm):
        "Restore firmware configuration."
        ### Restore ConfigUCI ###
        config = orm.Config.objects.get()
        orm.ConfigUCI.objects.filter(section='registry registry', option='base_uri', config=config).delete()
        orm.ConfigUCI.objects.filter(section='registry registry', option='cert', config=config).delete()
        # TODO (eventually) restore old config uci #245 note-25
        # orm.ConfigUCI.objects.create(section='server server', option='base_path',
        #   value="'/api'", config=config)

        ### Restore Config file /etc/config/confine ###
        cfile = orm.ConfigFile.objects.get(path='/etc/config/confine')
        new_content = cfile.content.replace(", 'registry registry'])", "])")
        assert 'registry registry' not in new_content
        cfile.content = new_content
        cfile.save()
        

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
            'node': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'keys'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['nodes.Node']"}),
            'ssh_auth': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ssh_pass': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
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
