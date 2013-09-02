# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ConfigFile.chmod'
        db.delete_column(u'firmware_configfile', 'chmod')

        # Adding field 'ConfigFile.mode'
        db.add_column(u'firmware_configfile', 'mode',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=6, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'ConfigFile.chmod'
        db.add_column(u'firmware_configfile', 'chmod',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=6, blank=True),
                      keep_default=False)

        # Deleting field 'ConfigFile.mode'
        db.delete_column(u'firmware_configfile', 'mode')


    models = {
        u'communitynetworks.cnhost': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'CnHost'},
            'app_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'cndb_cached_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cndb_uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'firmware.baseimage': {
            'Meta': {'object_name': 'BaseImage'},
            'architectures': ('controller.models.fields.MultiSelectField', [], {'max_length': '250'}),
            'config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['firmware.Config']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        u'firmware.build': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Build'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('privatefiles.models.fields.PrivateFileField', [], {'max_length': '100'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['nodes.Node']", 'unique': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'firmware.buildfile': {
            'Meta': {'unique_together': "(['build', 'path'],)", 'object_name': 'BuildFile'},
            'build': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['firmware.Build']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'firmware.builduci': {
            'Meta': {'unique_together': "(['build', 'section', 'option'],)", 'object_name': 'BuildUCI'},
            'build': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['firmware.Build']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'section': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'firmware.config': {
            'Meta': {'object_name': 'Config'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'firmware.configfile': {
            'Meta': {'unique_together': "(['config', 'path'],)", 'object_name': 'ConfigFile'},
            'config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['firmware.Config']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'optional': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'firmware.configuci': {
            'Meta': {'unique_together': "(['config', 'section', 'option'],)", 'object_name': 'ConfigUCI'},
            'config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['firmware.Config']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'section': ('django.db.models.fields.CharField', [], {'default': "'node'", 'max_length': '32'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'arch': ('django.db.models.fields.CharField', [], {'default': "'x86_64'", 'max_length': '16'}),
            'boot_sn': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'cert': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_iface': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'priv_ipv4_prefix': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'install_conf'", 'max_length': '16'}),
            'sliver_mac_prefix': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv4': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '8'}),
            'sliver_pub_ipv4_range': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv6': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '8'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'tinc.island': {
            'Meta': {'object_name': 'Island'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'tinc.tincaddress': {
            'Meta': {'object_name': 'TincAddress'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tinc.Island']"}),
            'port': ('django.db.models.fields.SmallIntegerField', [], {'default': "'666'"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tinc.TincServer']"})
        },
        u'tinc.tincclient': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'TincClient'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tinc.Island']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True', 'blank': 'True'})
        },
        u'tinc.tincserver': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'TincServer'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True', 'blank': 'True'})
        },
        u'users.group': {
            'Meta': {'object_name': 'Group'},
            'allow_nodes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_slices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['firmware']