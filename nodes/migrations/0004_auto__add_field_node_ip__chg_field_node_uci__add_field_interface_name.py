# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Node.ip'
        db.add_column('nodes_node', 'ip',
                      self.gf('django.db.models.fields.IPAddressField')(default='1.1.1.1', max_length=15),
                      keep_default=False)


        # Changing field 'Node.uci'
        db.alter_column('nodes_node', 'uci', self.gf('django.db.models.fields.TextField')())
        # Adding field 'Interface.name'
        db.add_column('nodes_interface', 'name',
                      self.gf('django.db.models.fields.CharField')(default='eth1', max_length=8),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Node.ip'
        db.delete_column('nodes_node', 'ip')


        # Changing field 'Node.uci'
        db.alter_column('nodes_node', 'uci', self.gf('django.db.models.fields.files.FileField')(max_length=100))
        # Deleting field 'Interface.name'
        db.delete_column('nodes_interface', 'name')

    models = {
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
        'nodes.interface': {
            'Meta': {'object_name': 'Interface'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'802.11a/b/g/n'", 'max_length': '255'})
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
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'latitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'public_key': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'}),
            'uci': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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