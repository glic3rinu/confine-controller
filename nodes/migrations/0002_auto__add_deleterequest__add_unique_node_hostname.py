# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DeleteRequest'
        db.create_table('nodes_deleterequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
        ))
        db.send_create_signal('nodes', ['DeleteRequest'])

        # Adding unique constraint on 'Node', fields ['hostname']
        db.create_unique('nodes_node', ['hostname'])

    def backwards(self, orm):
        # Removing unique constraint on 'Node', fields ['hostname']
        db.delete_unique('nodes_node', ['hostname'])

        # Deleting model 'DeleteRequest'
        db.delete_table('nodes_deleterequest')

    models = {
        'nodes.communitylink': {
            'Meta': {'object_name': 'CommunityLink', '_ormbases': ['nodes.Link']},
            'link_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Link']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.cpu': {
            'Meta': {'object_name': 'CPU'},
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': "'1'"})
        },
        'nodes.deleterequest': {
            'Meta': {'object_name': 'DeleteRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"})
        },
        'nodes.directlink': {
            'Meta': {'object_name': 'DirectLink', '_ormbases': ['nodes.Link']},
            'link_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Link']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.gatewaylink': {
            'Meta': {'object_name': 'GatewayLink', '_ormbases': ['nodes.Link']},
            'link_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Link']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.link': {
            'Meta': {'object_name': 'Link'},
            'connected_to': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'connected_to'", 'blank': 'True', 'to': "orm['nodes.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'})
        },
        'nodes.locallink': {
            'Meta': {'object_name': 'LocalLink', '_ormbases': ['nodes.Link']},
            'link_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Link']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.memory': {
            'Meta': {'object_name': 'Memory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'architecture': ('django.db.models.fields.CharField', [], {'default': "'x86_generic'", 'max_length': '128'}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'public_key': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'}),
            'uci': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'nodes.storage': {
            'Meta': {'object_name': 'Storage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'types': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['nodes']