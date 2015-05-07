# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SliverLog'
        db.create_table(u'journal_sliverlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slice', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, on_delete=models.SET_NULL, to=orm['slices.Slice'])),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['nodes.Node'])),
            ('created_on', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('expires_on', self.gf('django.db.models.fields.DateField')(null=True)),
            ('data', self.gf('jsonfield.fields.JSONField')()),
        ))
        db.send_create_signal(u'journal', ['SliverLog'])


    def backwards(self, orm):
        # Deleting model 'SliverLog'
        db.delete_table(u'journal_sliverlog')


    models = {
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
        u'journal.sliverlog': {
            'Meta': {'object_name': 'SliverLog'},
            'created_on': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {}),
            'expires_on': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['nodes.Node']"}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['slices.Slice']"})
        },
        u'slices.slice': {
            'Meta': {'object_name': 'Slice'},
            'allow_isolated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2015, 5, 20, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'slices'", 'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_sn': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'isolated_vlan_tag': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'register'", 'max_length': '16'})
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

    complete_apps = ['journal']
