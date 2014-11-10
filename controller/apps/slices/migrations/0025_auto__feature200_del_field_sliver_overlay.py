# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Sliver.overlay_sha256'
        db.delete_column(u'slices_sliver', 'overlay_sha256')

        # Deleting field 'Sliver.overlay_uri'
        db.delete_column(u'slices_sliver', 'overlay_uri')

        # Deleting field 'Sliver.overlay'
        db.delete_column(u'slices_sliver', 'overlay')

        # Deleting field 'SliverDefaults.overlay_sha256'
        db.delete_column(u'slices_sliverdefaults', 'overlay_sha256')

        # Deleting field 'SliverDefaults.overlay_uri'
        db.delete_column(u'slices_sliverdefaults', 'overlay_uri')

        # Deleting field 'SliverDefaults.overlay'
        db.delete_column(u'slices_sliverdefaults', 'overlay')


    def backwards(self, orm):
        # Adding field 'Sliver.overlay_sha256'
        db.add_column(u'slices_sliver', 'overlay_sha256',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True),
                      keep_default=False)

        # Adding field 'Sliver.overlay_uri'
        db.add_column(u'slices_sliver', 'overlay_uri',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True),
                      keep_default=False)

        # Adding field 'Sliver.overlay'
        db.add_column(u'slices_sliver', 'overlay',
                      self.gf('django.db.models.fields.files.FileField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'SliverDefaults.overlay_sha256'
        db.add_column(u'slices_sliverdefaults', 'overlay_sha256',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True),
                      keep_default=False)

        # Adding field 'SliverDefaults.overlay_uri'
        db.add_column(u'slices_sliverdefaults', 'overlay_uri',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True),
                      keep_default=False)

        # Adding field 'SliverDefaults.overlay'
        db.add_column(u'slices_sliverdefaults', 'overlay',
                      self.gf('django.db.models.fields.files.FileField')(default='', max_length=100, blank=True),
                      keep_default=False)


    models = {
        u'nodes.directiface': {
            'Meta': {'unique_together': "(['name', 'node'],)", 'object_name': 'DirectIface'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'direct_ifaces'", 'to': u"orm['nodes.Node']"})
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
        u'slices.slice': {
            'Meta': {'object_name': 'Slice'},
            'allow_isolated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 12, 10, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'slices'", 'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_sn': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'isolated_vlan_tag': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'register'", 'max_length': '16'})
        },
        u'slices.sliceprop': {
            'Meta': {'unique_together': "(('slice', 'name'),)", 'object_name': 'SliceProp'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': u"orm['slices.Slice']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'slices.sliver': {
            'Meta': {'unique_together': "(('slice', 'node'),)", 'object_name': 'Sliver'},
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'data_sha256': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'data_uri': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_sn': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'slivers'", 'to': u"orm['nodes.Node']"}),
            'set_state': ('controller.models.fields.NullableCharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'slivers'", 'to': u"orm['slices.Slice']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['slices.Template']", 'null': 'True', 'blank': 'True'})
        },
        u'slices.sliverdefaults': {
            'Meta': {'object_name': 'SliverDefaults'},
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'data_sha256': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'data_uri': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_sn': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'start'", 'max_length': '16'}),
            'slice': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'sliver_defaults'", 'unique': 'True', 'to': u"orm['slices.Slice']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['slices.Template']"})
        },
        u'slices.sliveriface': {
            'Meta': {'unique_together': "(('sliver', 'name'),)", 'object_name': 'SliverIface'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'nr': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodes.DirectIface']", 'null': 'True', 'blank': 'True'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'interfaces'", 'to': u"orm['slices.Sliver']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'slices.sliverprop': {
            'Meta': {'unique_together': "(('sliver', 'name'),)", 'object_name': 'SliverProp'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': u"orm['slices.Sliver']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'slices.template': {
            'Meta': {'object_name': 'Template'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'image_sha256': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'image_uri': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'node_archs': ('controller.models.fields.MultiSelectField', [], {'default': "'i686'", 'max_length': '256'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32'})
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

    complete_apps = ['slices']