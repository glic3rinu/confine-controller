# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'State.ssl_verified'
        db.add_column(u'state_state', 'ssl_verified',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'State.ssl_verified'
        db.delete_column(u'state_state', 'ssl_verified')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        u'state.nodesoftwareversion': {
            'Meta': {'object_name': 'NodeSoftwareVersion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'soft_version'", 'unique': 'True', 'to': u"orm['nodes.Node']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'state.state': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'State'},
            'add_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_contact_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_seen_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_try_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ssl_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'state.statehistory': {
            'Meta': {'ordering': "('-start',)", 'object_name': 'StateHistory'},
            'data': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'history'", 'to': u"orm['state.State']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '32'})
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

    complete_apps = ['state']
